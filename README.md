
# Brain-Chain: Multi-AI Agent Workflow System 🧠⚡

 Demo : http://184.72.86.185:3000/

Brain-Chain is a sophisticated multi-agent system that leverages specialized AI agents working in concert to process complex queries. The system features a supervisor agent that orchestrates workflow between enhancer, researcher, and coder agents to deliver comprehensive responses.


![image](https://github.com/user-attachments/assets/cebe5db1-069e-4912-a4f4-48286764db4d)



## Features ✨

- **Multi-Agent Architecture**: Specialized agents for different tasks
- **Dynamic Workflow Routing**: Intelligent task delegation based on query analysis
- **Real-time Processing**: Fast response times with Groq's LLama 3 70B model
- **Beautiful UI**: Streamlit-based interface with dark mode and agent visualization
- **Dockerized Deployment**: Easy setup with Docker Compose

## System Components 🛠️

### Agents
- **Supervisor** 👨‍💼: Orchestrates the workflow between agents
- **Enhancer** 🔍: Refines and clarifies user queries
- **Researcher** 📚: Gathers information using Tavily search
- **Coder** 💻: Executes code and performs calculations
- **Validator** ✅: Ensures response quality

### Technical Stack
- **Backend**: FastAPI with LangGraph workflow
- **Frontend**: Streamlit with custom UI components
- **LLM**: Groq's LLama 3 70B model
- **Tools**: Tavily Search, Riza Code Interpreter

## Getting Started 🚀

### Prerequisites
- Docker
- Docker Compose
- API keys for:
  - Groq
  - Riza
  - Tavily

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/srijan-op/brain-chain.git
   cd brain-chain
   ```

2. Create a `.env` file in the root directory with your API keys:
   ```env
   GROQ_API_KEY=your_groq_api_key
   RIZA_API_KEY=your_riza_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

4. Access the application:
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000

## Usage 📖

1. Enter your query in the text area
2. Click "Process Query"
3. Watch as the agents work together to:
   - Enhance your query
   - Research information
   - Perform calculations
   - Validate the response

The conversation history will display the workflow between agents.

## Project Structure 📂

```
brain-chain/
├── backend/
│   ├── Dockerfile
│   ├── main.py          # FastAPI application
│   ├── workflow.py      # Agent workflow logic
│   └── __init__.py
├── frontend/
│   ├── Dockerfile
│   ├── app.py           # Streamlit application
│   └── static/          # Static assets (logo)
├── .dockerignore
├── docker-compose.yml   # Docker configuration
├── requirements.txt     # Python dependencies
└── README.md
```

## API Endpoints 🤖

### POST `/process`
Process a user query through the agent workflow.

**Request:**
```json
{
  "text": "Your query here"
}
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "messages": [
      {"role": "human", "content": "Original query"},
      {"role": "agent", "name": "enhancer", "content": "Enhanced query"},
      {"role": "agent", "name": "researcher", "content": "Research findings"},
      {"role": "agent", "name": "coder", "content": "Code results"},
      {"role": "agent", "name": "validator", "content": "Validation"}
    ]
  }
}
```
