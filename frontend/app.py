# frontend/app.py
import streamlit as st
import requests
import json
import base64
from io import BytesIO
import time
from PIL import Image
import base64
import os

BACKEND_URL = "http://brainchain-backend:8000"
# Updated brand colors to match the logo
BRAND_COLOR_TEAL = "#4DDBBA"
BRAND_COLOR_PURPLE = "#9370DB"  # Close match to the purple in the logo

# Agent colors from Image 2
AGENT_COLORS = {
    "Supervisor": "#FFA500",  # Orange
    "Enhancer": "#3498DB",    # Blue
    "Researcher": "#4682B4",  # Steel Blue
    "Coder": "#32CD32",       # Lime Green
    "Validator": "#32CD32"    # Green
}

def format_message(message):
    """Format a message for display based on its attributes."""
    if message.get("name"):
        # This is an agent message - format with appropriate styling
        agent_name = message.get("name").upper()
        content = message.get("content", "")
        
        if agent_name == "RESEARCHER":
            return st.info(f"**{agent_name}**: {content}")
        elif agent_name == "SUPERVISOR":
            return st.warning(f"**{agent_name}**: {content}")
        elif agent_name == "CODER":
            return st.success(f"**{agent_name}**: {content}")
        elif agent_name == "VALIDATOR":
            return st.info(f"**{agent_name}**: {content}")
        elif agent_name == "ENHANCER":
            return st.warning(f"**{agent_name}**: {content}")
        else:
            return st.write(f"**{agent_name}**: {content}")
    else:
        # This is a user message or another type
        if message.get("type") == "human":
            return st.write(f"**YOU**: {message.get('content', '')}")
        else:
            return st.write(message.get("content", ""))

# Function to load the brain-chain logo as base64
def get_brain_chain_logo_base64():
    # This is a placeholder - you'll need to replace with actual logo data
    # For now, we'll use a URL, but in production you might want to include the image directly
    return "logo2.png"


# Add this function above your `main()` if not already
def get_base64_of_image(image_path):
    with open(image_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode()
    return b64_string


def main():
    st.set_page_config(
        page_title="Brain-Chain",
        page_icon="🧠",
        layout="wide"
    )
    
    # Custom CSS to improve UI - with dark mode colors and updated brand colors
    st.markdown(f"""
    <style>
    .main {{
        background-color: #1E1E1E;
        color: #E0E0E0;
    }}
    .stTextArea textarea {{
        border-radius: 10px;
        border: 1px solid {BRAND_COLOR_TEAL};
        padding: 10px;
        background-color: #2D2D2D;
        color: #E0E0E0;
    }}
    .stButton button {{
        border-radius: 10px;
        background: linear-gradient(135deg, {BRAND_COLOR_TEAL} 0%, {BRAND_COLOR_PURPLE} 100%);
        color: white;
        font-weight: bold;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
        border: none;
    }}
    .stButton button:hover {{
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        transform: translateY(-2px);
    }}
    div.stSuccess, div.stInfo, div.stWarning {{
        border-radius: 10px;
        margin: 10px 0;
        padding: 15px;
    }}
    h1, h2, h3 {{
        color: #E0E0E0;
    }}
    .chat-container {{
        border-radius: 10px;
        background-color: #2D2D2D;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        color: #E0E0E0;
    }}
    .stMarkdown {{
        color: #E0E0E0;
    }}
    /* Change the color of the form container */
    [data-testid="stForm"] {{
        background-color: #2D2D2D;
        padding: 20px;
        border-radius: 10px;
        color: #E0E0E0;
    }}
    /* Ensure text in widgets is visible */
    .stTextInput input, .stNumberInput input, .stSelectbox select {{
        background-color: #383838;
        color: #E0E0E0;
        border: 1px solid #4F4F4F;
    }}
    /* Fix checkbox and radio button text */
    .stCheckbox label, .stRadio label {{
        color: #E0E0E0;
    }}
    /* Adjust sidebar colors */
    [data-testid="stSidebar"] {{
        background-color: #1E1E1E;
        color: #E0E0E0;
    }}
    /* Adjust expander colors */
    .stExpander {{
        background-color: #2D2D2D;
        border-radius: 10px;
    }}
    /* Input label colors */
    label {{
        color: #E0E0E0 !important;
    }}
    /* For any card-like elements */
    .css-card {{
        background-color: #2D2D2D;
        padding: 20px;
        border-radius: 10px;
        color: #E0E0E0;
        margin-bottom: 10px;
    }}
    /* Horizontal divider */
    hr {{
        border-color: #4F4F4F;
    }}
    /* Style the colored header if used */
    [data-testid="stHeader"] {{
        background-color: #2D2D2D;
        color: {BRAND_COLOR_TEAL};
    }}
    /* Center logo in sidebar */
    .sidebar-logo {{
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }}
    /* Gradient text for title */
    .gradient-text {{
        background: linear-gradient(to right, {BRAND_COLOR_TEAL}, {BRAND_COLOR_PURPLE});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline;
    }}
    /* Apply some animation to key elements */
    @keyframes glow {{
        0% {{
            box-shadow: 0 0 5px {BRAND_COLOR_TEAL}50;
        }}
        50% {{
            box-shadow: 0 0 20px {BRAND_COLOR_TEAL}50;
        }}
        100% {{
            box-shadow: 0 0 5px {BRAND_COLOR_TEAL}50;
        }}
    }}
    .glow-effect {{
        animation: glow 2s infinite;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Animated title with gradient using both brand colors
    st.markdown(
        f"""
        <div style="text-align: center; padding: 10px;">
            <h1 class="gradient-text" style="font-size: 42px; font-weight: bold;">
                🧠 Brain-Chain
            </h1>
            <p style="font-size: 18px; color: #B0B0B0;">
                Linked Intelligence Network with Agents in Action
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize session state for chat history and user input
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""

    # Function to reset the input box
    def reset_input():
        st.session_state.user_input = ""

    # Display chat history
    if st.session_state.chat_history:
        st.subheader("Conversation History")
        st.markdown(f'<hr style="height:3px;border:none;background:linear-gradient(to right, {BRAND_COLOR_TEAL}, {BRAND_COLOR_PURPLE});margin-bottom:20px;">', unsafe_allow_html=True)
        
        chat_container = st.container()
        with chat_container:
            for i, exchange in enumerate(st.session_state.chat_history):
                st.markdown(f"""
                <div style="background-color: #383838; padding: 10px; border-radius: 10px; margin-bottom: 10px;">
                    <p style="font-weight: bold; color: {BRAND_COLOR_TEAL};">YOU:</p>
                    <p style="margin-left: 10px; color: #E0E0E0;">{exchange.get("query", "")}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if "messages" in exchange.get("response", {}):
                    # Skip the first message which is the user query (already displayed)
                    for message in exchange["response"]["messages"][1:]:
                        format_message(message)
                st.markdown('<hr style="border-color:#4F4F4F;margin:20px 0;">', unsafe_allow_html=True)

    # Create a card-like container for the input form with dark theme colors
    st.markdown(f"""
    <div style="background-color: #2D2D2D; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);" class="glow-effect">
        <h3 style="background: linear-gradient(to right, {BRAND_COLOR_TEAL}, {BRAND_COLOR_PURPLE}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 15px;">Ask the Brain-Chain</h3>
    </div>
    """, unsafe_allow_html=True)

    with st.form("query_form", clear_on_submit=True):
        user_input = st.text_area("Enter your query:", 
                                  value=st.session_state.user_input, 
                                  height=100, 
                                  key="query_input",
                                  placeholder="Type your question here... Brain-Chain will process it using its specialized agents.")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submitted = st.form_submit_button("Process Query 🚀", on_click=reset_input)

        if submitted and user_input:
            with st.spinner("🧠 Agents working on your query..."):
                try:
                    # Add a brief delay for visual effect
                    time.sleep(0.5)
                    
                    response = requests.post(
                        f"{BACKEND_URL}/process",
                        json={"text": user_input}
                    )

                    if response.status_code == 200:
                        result = response.json()
                        
                        # Add to chat history
                        st.session_state.chat_history.append({
                            "query": user_input,
                            "response": result["result"]
                        })
                        
                        # Display success and rerun to update the chat history display
                        st.success("Processing Complete ✅")
                        st.rerun()
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Connection error: {e}")

    # Add sidebar with information - dark theme with updated brand color
    with st.sidebar:
        # Display the Brain-Chain logo centered in the sidebar
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, "static", "logo2.png")
        logo_base64 = get_base64_of_image(logo_path)

        st.markdown(f"""
        <div class="sidebar-logo">
            <img src="data:image/png;base64,{logo_base64}" width="200">
         </div>
        """, unsafe_allow_html=True)
        
        st.subheader("About Brain-Chain")
        st.markdown(f'<hr style="height:3px;border:none;background:linear-gradient(to right, {BRAND_COLOR_TEAL}, {BRAND_COLOR_PURPLE});margin-bottom:20px;">', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background-color: #2D2D2D; padding: 15px; border-radius: 10px; margin-bottom: 20px; color: #E0E0E0;">
            <p>A multi-agent architecture consisting of specialized agents working together to solve complex problems:</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Agent cards with individual colors restored from Image 2
        agent_data = [
            {"name": "Supervisor", "emoji": "👨‍💼", "desc": "Directs workflow and routes tasks", "color": "#FFA500"},
            {"name": "Enhancer", "emoji": "🔍", "desc": "Clarifies and refines ambiguous queries", "color": "#FF6347"},
            {"name": "Researcher", "emoji": "📚", "desc": "Gathers information for knowledge-based questions", "color": "#4682B4"},
            {"name": "Coder", "emoji": "💻", "desc": "Handles technical calculations and code execution", "color": "#32CD32"},
            {"name": "Validator", "emoji": "✅", "desc": "Ensures quality and completeness of responses", "color": "#9370DB"}
        ]
        
        for agent in agent_data:
            st.markdown(f"""
            <div style="background-color: #2D2D2D; border-left: 5px solid {agent['color']}; padding: 10px; border-radius: 5px; margin-bottom: 10px; color: #E0E0E0;">
                <p style="font-weight: bold; margin-bottom: 5px;">{agent['emoji']} {agent['name']}</p>
                <p style="font-size: 0.9em; color: #B0B0B0;">{agent['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
        


if __name__ == "__main__":
    main()