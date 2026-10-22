import requests
import streamlit as st

# -----------------------------
# Configuration
# -----------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"

# -----------------------------
# Page configuration
# -----------------------------

st.set_page_config(
    page_title="JARVIS - Offline AI Assistant",
    page_icon="⚡",
    layout="wide"
)

# -----------------------------
# Styling
# -----------------------------

st.markdown("""
<style>
    .main-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 0;
    }

    .subtitle {
        color: #888;
        margin-top: 0;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Session state
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "mode" not in st.session_state:
    st.session_state.mode = "General"

# -----------------------------
# AI function
# -----------------------------

def ask_jarvis(messages, mode):

    system_prompts = {
        "General": """
You are JARVIS, a helpful offline AI assistant.
Give clear, accurate and friendly answers.
""",

        "Study": """
You are JARVIS, a college study assistant.
Explain difficult concepts in simple language.
Use examples, structured explanations and step-by-step reasoning.
Help the student learn instead of simply giving answers.
""",

        "Coding": """
You are JARVIS, a programming assistant.
Help students understand programming concepts,
write code, debug code and explain errors clearly.
When providing code, explain what it does.
"""
    }

    conversation = system_prompts[mode] + "\n\n"

    for message in messages:
        role = message["role"]
        content = message["content"]

        if role == "user":
            conversation += f"Student: {content}\n"
        else:
            conversation += f"JARVIS: {content}\n"

    conversation += "JARVIS:"

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": conversation,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()

    return response.json()["response"]


# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:

    st.markdown("## ⚡ JARVIS")

    st.caption("Offline AI Assistant")

    st.divider()

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("### Assistant Mode")

    mode = st.radio(
        "Choose mode:",
        ["General", "Study", "Coding"],
        index=["General", "Study", "Coding"].index(
            st.session_state.mode
        )
    )

    st.session_state.mode = mode

    st.divider()

    st.markdown("### System")

    st.success("● Offline")

    st.caption("Model: Llama 3.2 3B")
    st.caption("Engine: Ollama")

# -----------------------------
# Main area
# -----------------------------

st.markdown(
    '<p class="main-title">⚡ JARVIS</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">Your private offline AI assistant</p>',
    unsafe_allow_html=True
)

st.divider()

# -----------------------------
# Welcome message
# -----------------------------

if not st.session_state.messages:

    st.markdown("### Hello! 👋")

    st.write(
        "I'm JARVIS, your offline AI assistant. "
        "I can help with studying, programming and general questions."
    )

    st.info(
        "Everything currently runs locally through Ollama."
    )

# -----------------------------
# Display conversation
# -----------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------
# Chat input
# -----------------------------

user_input = st.chat_input("Ask JARVIS anything...")

if user_input:

    # Display user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response
    with st.chat_message("assistant"):

        with st.spinner("JARVIS is thinking..."):

            try:

                answer = ask_jarvis(
                    st.session_state.messages,
                    st.session_state.mode
                )

                st.markdown(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:

                st.error(
                    "Could not connect to Ollama. "
                    "Make sure Ollama is running."
                )

                st.caption(str(e))