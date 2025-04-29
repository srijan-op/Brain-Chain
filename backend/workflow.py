

# backend/workflow.py
import os
from typing import Annotated, Sequence, List, Literal
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools.riza.command import ExecPython
from langchain_groq import ChatGroq
from langgraph.types import Command
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import create_react_agent

# Load API keys (ensure they are set in the environment)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
RIZA_API_KEY = os.environ.get("RIZA_API_KEY")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY")

if not all([GROQ_API_KEY, RIZA_API_KEY, TAVILY_API_KEY]):
    raise ValueError("Ensure GROQ_API_KEY, RIZA_API_KEY and TAVILY_API_KEY are set as environment variables.")

# Initialize LLM
llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama-3.3-70b-versatile")

# Define Tools
tool_tavily = TavilySearchResults(max_results=2)
tool_code_interpreter = ExecPython()
tools = [tool_tavily, tool_code_interpreter]

# Define Supervisor Agent
system_prompt = ('''You are a workflow supervisor managing a team of three agents: Prompt Enhancer, Researcher, and Coder. Your role is to direct the flow of tasks by selecting the next agent based on the current stage of the workflow. For each task, provide a clear rationale for your choice, ensuring that the workflow progresses logically, efficiently, and toward a timely completion.

**Team Members**:
1. Enhancer: Use prompt enhancer as the first preference, to Focuse on clarifying vague or incomplete user queries, improving their quality, and ensuring they are well-defined before further processing.
2. Researcher: Specializes in gathering information.
3. Coder: Handles technical tasks related to caluclation, coding, data analysis, and problem-solving, ensuring the correct implementation of solutions.

**Responsibilities**:
1. Carefully review each user request and evaluate agent responses for relevance and completeness.
2. Continuously route tasks to the next best-suited agent if needed.
3. Ensure the workflow progresses efficiently, without terminating until the task is fully resolved.

Your goal is to maximize accuracy and effectiveness by leveraging each agent’s unique expertise while ensuring smooth workflow execution.
''')

# Define a Supervisor class to specify the next worker in the pipeline
class Supervisor(BaseModel):
    next: Literal["enhancer", "researcher", "coder"] = Field(
        description="Specifies the next worker in the pipeline: "
                    "'enhancer' for enhancing the user prompt if it is unclear or vague, "
                    "'researcher' for additional information gathering, "
                    "'coder' for solving technical or code-related problems."
    )
    reason: str = Field(
        description="The reason for the decision, providing context on why a particular worker was chosen."
    )

def supervisor_node(state: MessagesState) -> Command[Literal["enhancer", "researcher", "coder"]]:
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]
    response = llm.with_structured_output(Supervisor).invoke(messages)
    goto = response.next
    reason = response.reason
    print(f"Current Node: Supervisor -> Goto: {goto}")
    return Command(
        update={"messages": [HumanMessage(content=reason, name="supervisor")]},
        goto=goto,
    )

# Define Enhancer Agent
def enhancer_node(state: MessagesState) -> Command[Literal["supervisor"]]:
        system_prompt = (
        "You are an advanced query enhancer. Your task is to:\n"
        "Don't ask anything to the user, select the most appropriate prompt"
        "1. Clarify and refine user inputs.\n"
        "2. Identify any ambiguities in the query.\n"
        "3. Generate a more precise and actionable version of the original request.\n"
    )
        messages = [{"role": "system", "content": system_prompt}] + state["messages"]
        enhanced_query = llm.invoke(messages).content
        print(f"Current Node: Enhancer -> Goto: supervisor")
        return Command(
        update={
            "messages": [
                HumanMessage(content=enhanced_query, name="enhancer")
            ]
        },
        goto="supervisor",
    )

# Define Researcher Agent
def research_node(state: MessagesState) -> Command[Literal["validator"]]:
    research_agent = create_react_agent(
        llm,
        tools=[tool_tavily],
        state_modifier="You are a researcher. Focus on gathering information and generating content. Do not perform any other tasks"  # Instruction to restrict the agent's behavior
    )
    result = research_agent.invoke(state)
    print(f"Current Node: Researcher -> Goto: validator")
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="researcher")
            ]
        },
        goto="validator",
    )

# Define Coder Agent
def code_node(state: MessagesState) -> Command[Literal["validator"]]:
    code_agent = create_react_agent(
        llm,
        tools=[tool_code_interpreter],
        state_modifier=("You are a coder and analyst. Focus on mathematical caluclations, analyzing, solving math questions, "
            "and executing code. Handle technical problem-solving and data tasks."
    )
    )
    result = code_agent.invoke(state)
    print(f"Current Node: Coder -> Goto: validator")
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="coder")
            ]
        },
        goto="validator",
    )

# Define Validator Agent

class Validator(BaseModel):
    next: Literal["supervisor", "FINISH"] = Field(
        description="Specifies the next worker in the pipeline: 'supervisor' to continue or 'FINISH' to terminate."
    )
    reason: str = Field(
        description="The reason for the decision."
    )



validator_system_prompt = '''
You are a workflow validator. Your task is to ensure the quality of the workflow. Specifically, you must:
- Review the user's question (the first message in the workflow).
- Review the answer (the last message in the workflow).
- If the answer satisfactorily addresses the question, signal to end the workflow.
- If the answer is inappropriate or incomplete, signal to route back to the supervisor for re-evaluation or further refinement.
Ensure that the question and answer match logically and the workflow can be concluded or continued based on this evaluation.

Routing Guidelines:
1. 'supervisor' Agent: For unclear or vague state messages.
2. Respond with 'FINISH' to end the workflow.
'''

class Validator(BaseModel):
    next: Literal["supervisor", "FINISH"] = Field(description="Specifies the next worker in the pipeline: 'supervisor' to continue or 'FINISH' to terminate.")
    reason: str = Field(description="The reason for the decision.")

def validator_node(state: MessagesState) -> Command[Literal["supervisor", "__end__"]]:
    user_question = state["messages"][0].content
    agent_answer = state["messages"][-1].content
    messages = [
        {"role": "system", "content": validator_system_prompt},
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": agent_answer},
    ]
    response = llm.with_structured_output(Validator).invoke(messages)
    goto = response.next
    reason = response.reason
    if goto == "FINISH" or goto == END:
        goto = END
        print("Transitioning to END")
    else:
        print(f"Current Node: Validator -> Goto: Supervisor")
    return Command(
        update={
            "messages": [
                HumanMessage(content=reason, name="validator")
            ]
        },
        goto=goto,
    )

# Define the Workflow Graph
def create_workflow():
    # Initialize the StateGraph with MessagesState to manage the flow of messages between nodes
    builder = StateGraph(MessagesState)


    builder.add_node("supervisor", supervisor_node)  # Add the supervisor node to the graph
    # Add task-specific nodes for various roles in the multi-agent system
    builder.add_node("enhancer", enhancer_node)  # Node for refining and clarifying user inputs
    builder.add_node("researcher", research_node)  # Node for handling research-related tasks
    builder.add_node("coder", code_node)  # Node for managing coding and analytical tasks
    builder.add_node("validator", validator_node)  # Node for managing coding and analytical tasks

    # Add edges and nodes to define the workflow of the graph
    builder.add_edge(START, "supervisor")  # Connect the start node to the supervisor node
    # Compile the graph to finalize its structure
    graph = builder.compile()
    return graph

# Main function to run the workflow
def run_workflow(user_query: str):
    workflow = create_workflow()
    inputs = {"messages": [HumanMessage(content=user_query)]}
    results = workflow.invoke(inputs)
    return results

if __name__ == "__main__":
    # Example usage:
    user_query = "What is the GDP growth rate of USA"
    result = run_workflow(user_query)
    print(result)
