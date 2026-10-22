import uuid

import streamlit as st

from core.ai import ask_jarvis

from memory.database import (
    create_conversation,
    save_message,
    load_messages,
    get_conversations,
    update_conversation_title,
    save_memory,
    get_memories_with_ids,
    find_memory,
    delete_memory,
    get_relevant_memories,
)

from documents.pdf_reader import extract_pdf_text

from documents.retriever import (
    create_chunks,
    find_relevant_chunks,
)

from study.study_tools import run_study_action

from coding.coding_tools import run_coding_action

from tools.local_tools import run_local_tool


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="JARVIS - Offline AI Assistant",
    page_icon="⚡",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "session_id" not in st.session_state:

    st.session_state.session_id = str(uuid.uuid4())

    create_conversation(
        st.session_state.session_id
    )


if "messages" not in st.session_state:

    st.session_state.messages = load_messages(
        st.session_state.session_id
    )


if "mode" not in st.session_state:

    st.session_state.mode = "General"


if "document_text" not in st.session_state:

    st.session_state.document_text = ""


if "document_name" not in st.session_state:

    st.session_state.document_name = ""


if "study_action" not in st.session_state:

    st.session_state.study_action = "Explain"


if "study_result" not in st.session_state:

    st.session_state.study_result = ""


if "coding_action" not in st.session_state:

    st.session_state.coding_action = "Generate Code"


if "coding_language" not in st.session_state:

    st.session_state.coding_language = "Python"


if "coding_result" not in st.session_state:

    st.session_state.coding_result = ""


if "tool_name" not in st.session_state:

    st.session_state.tool_name = ""


if "tool_active" not in st.session_state:

    st.session_state.tool_active = False


if "tool_result" not in st.session_state:

    st.session_state.tool_result = ""


# ============================================================
# CHAT FUNCTIONS
# ============================================================

def start_new_chat():

    new_session_id = str(uuid.uuid4())

    create_conversation(
        new_session_id
    )

    st.session_state.session_id = new_session_id

    st.session_state.messages = []

    st.session_state.document_text = ""

    st.session_state.document_name = ""

    st.session_state.study_result = ""

    st.session_state.coding_result = ""

    st.session_state.tool_name = ""

    st.session_state.tool_active = False

    st.session_state.tool_result = ""


def load_chat(session_id):

    st.session_state.session_id = session_id

    st.session_state.messages = load_messages(
        session_id
    )

    st.session_state.document_text = ""

    st.session_state.document_name = ""

    st.session_state.study_result = ""

    st.session_state.coding_result = ""

    st.session_state.tool_name = ""

    st.session_state.tool_active = False

    st.session_state.tool_result = ""


# ============================================================
# DOCUMENT FUNCTIONS
# ============================================================

def get_document_context(
    question,
    document_text,
):

    if not document_text:

        return ""

    chunks = create_chunks(
        document_text
    )

    relevant_chunks = find_relevant_chunks(
        question,
        chunks,
        top_k=3,
    )

    if not relevant_chunks:

        return ""

    return "\n\n".join(
        relevant_chunks
    )


# ============================================================
# MEMORY COMMANDS
# ============================================================

def handle_memory_command(user_input):

    text = user_input.strip()

    lower_text = text.lower()

    # --------------------------------------------------------
    # REMEMBER
    # --------------------------------------------------------

    remember_prefixes = [
        "remember that ",
        "remember ",
        "save this: ",
        "save this ",
    ]

    for prefix in remember_prefixes:

        if lower_text.startswith(prefix):

            memory = text[len(prefix):].strip()

            if not memory:

                return (
                    True,
                    "What would you like me to remember?",
                )

            save_memory(
                memory
            )

            return (
                True,
                f"🧠 I'll remember that: **{memory}**",
            )

    # --------------------------------------------------------
    # FORGET
    # --------------------------------------------------------

    forget_prefixes = [
        "forget that ",
        "forget ",
        "delete memory ",
    ]

    for prefix in forget_prefixes:

        if lower_text.startswith(prefix):

            search_text = text[len(prefix):].strip()

            if not search_text:

                return (
                    True,
                    "What would you like me to forget?",
                )

            matches = find_memory(
                search_text
            )

            if not matches:

                return (
                    True,
                    "I couldn't find a matching memory.",
                )

            if len(matches) == 1:

                memory_id, memory = matches[0]

                delete_memory(
                    memory_id
                )

                return (
                    True,
                    f"🧠 Forgotten: **{memory}**",
                )

            return (
                True,
                "I found multiple matching memories. "
                "Please remove the specific one from "
                "the Memory panel.",
            )

    return False, ""


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    st.markdown(
        "# ⚡ JARVIS"
    )

    st.caption(
        "Private Offline AI Assistant"
    )

    st.divider()

    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

    if st.button(
        "＋ New Chat",
        use_container_width=True,
    ):

        start_new_chat()

        st.rerun()

    # --------------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------------

    conversations = get_conversations()

    with st.expander(
        "💬 Chat History",
        expanded=False,
    ):

        if conversations:

            for (
                session_id,
                title,
                updated_at,
            ) in conversations[:15]:

                if st.button(
                    title,
                    key=f"chat_{session_id}",
                    use_container_width=True,
                ):

                    load_chat(
                        session_id
                    )

                    st.rerun()

        else:

            st.caption(
                "No previous conversations."
            )

    st.divider()

    # --------------------------------------------------------
    # ASSISTANT MODE
    # --------------------------------------------------------

    st.markdown(
        "### 🎯 Assistant Mode"
    )

    mode = st.radio(
        "Choose mode:",
        [
            "General",
            "Study",
            "Coding",
        ],
        index=[
            "General",
            "Study",
            "Coding",
        ].index(
            st.session_state.mode
        ),
    )

    st.session_state.mode = mode

    # --------------------------------------------------------
    # CLOSE TOOLS WHEN LEAVING GENERAL MODE
    # --------------------------------------------------------

    if mode != "General":

        st.session_state.tool_active = False

        st.session_state.tool_result = ""

        st.session_state.tool_name = ""

    # --------------------------------------------------------
    # STUDY MODE
    # --------------------------------------------------------

    if mode == "Study":

        st.markdown(
            "#### 📚 Study Tools"
        )

        study_action = st.selectbox(
            "Choose an action:",
            [
                "Explain",
                "Summarize",
                "Quiz",
                "Flashcards",
                "Important Questions",
                "Study Plan",
            ],
            key="study_action_select",
        )

        st.session_state.study_action = study_action

    # --------------------------------------------------------
    # CODING MODE
    # --------------------------------------------------------

    if mode == "Coding":

        st.markdown(
            "#### 💻 Coding Tools"
        )

        coding_action = st.selectbox(
            "Choose an action:",
            [
                "Generate Code",
                "Explain Code",
                "Debug Code",
                "Review Code",
                "Optimize Code",
                "Convert Code",
            ],
            key="coding_action_select",
        )

        coding_language = st.selectbox(
            "Programming language:",
            [
                "Python",
                "C",
                "C++",
                "Java",
                "JavaScript",
                "HTML/CSS",
                "SQL",
            ],
            key="coding_language_select",
        )

        st.session_state.coding_action = coding_action

        st.session_state.coding_language = coding_language

    # --------------------------------------------------------
    # LOCAL TOOLS
    # --------------------------------------------------------

    st.markdown(
        "### 🔧 Tools"
    )

    selected_tool = st.selectbox(
        "Choose a tool:",
        [
            "None",
            "Calculator",
            "Date & Time",
            "System Information",
            "File Information",
        ],
        key="tool_select",
    )

    if selected_tool == "None":

        st.session_state.tool_name = ""

        st.session_state.tool_active = False

        st.session_state.tool_result = ""

    else:

        st.session_state.tool_name = selected_tool

        if st.button(
            "🔧 Open Tool",
            use_container_width=True,
            key="open_tool_button",
        ):

            st.session_state.tool_active = True

            st.session_state.tool_result = ""

            st.rerun()

    # --------------------------------------------------------
    # DOCUMENTS
    # --------------------------------------------------------

    st.markdown(
        "### 📄 Documents"
    )

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        key="pdf_uploader",
    )

    if uploaded_file:

        if (
            st.session_state.document_name
            != uploaded_file.name
        ):

            with st.spinner(
                "Reading PDF..."
            ):

                try:

                    text = extract_pdf_text(
                        uploaded_file
                    )

                    st.session_state.document_text = text

                    st.session_state.document_name = (
                        uploaded_file.name
                    )

                    st.session_state.study_result = ""

                except Exception as error:

                    st.error(
                        "Could not read this PDF."
                    )

                    st.caption(
                        str(error)
                    )

        if st.session_state.document_text:

            st.success(
                "PDF loaded"
            )

            st.caption(
                f"📄 {st.session_state.document_name}"
            )

            word_count = len(
                st.session_state.document_text.split()
            )

            st.caption(
                f"{word_count:,} words"
            )

            if st.button(
                "Remove PDF",
                use_container_width=True,
                key="remove_pdf_button",
            ):

                st.session_state.document_text = ""

                st.session_state.document_name = ""

                st.session_state.study_result = ""

                st.rerun()

    # --------------------------------------------------------
    # STUDY ACTION BUTTON
    # --------------------------------------------------------

    if (
        mode == "Study"
        and st.session_state.document_text
    ):

        st.divider()

        if st.button(
            "📚 Run Study Tool",
            use_container_width=True,
            type="primary",
            key="run_study_tool_button",
        ):

            with st.spinner(
                "JARVIS is studying..."
            ):

                try:

                    result = run_study_action(
                        st.session_state.study_action,
                        st.session_state.document_text,
                    )

                    st.session_state.study_result = result

                except Exception as error:

                    st.session_state.study_result = ""

                    st.error(
                        "Study tool failed."
                    )

                    st.caption(
                        str(error)
                    )

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    st.divider()

    st.markdown(
        "### 🧠 Memory"
    )

    memories = get_memories_with_ids()

    if memories:

        st.caption(
            f"{len(memories)} saved memories"
        )

        with st.expander(
            "View & manage memories",
            expanded=False,
        ):

            for (
                memory_id,
                memory,
                created_at,
            ) in memories:

                st.write(
                    f"• {memory}"
                )

                if st.button(
                    "Delete",
                    key=f"delete_memory_{memory_id}",
                ):

                    delete_memory(
                        memory_id
                    )

                    st.rerun()

    else:

        st.caption(
            "No memories saved yet."
        )

    # --------------------------------------------------------
    # SYSTEM
    # --------------------------------------------------------

    st.divider()

    st.markdown(
        "### ⚙ System"
    )

    st.success(
        "● Offline"
    )

    st.caption(
        "Model: Llama 3.2 3B"
    )

    st.caption(
        "Engine: Ollama"
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    "# ⚡ JARVIS"
)

st.caption(
    "Your private offline AI assistant"
)

st.divider()


# ============================================================
# ACTIVE LOCAL TOOL
# ============================================================

if (
    st.session_state.mode == "General"
    and st.session_state.tool_active
    and st.session_state.tool_name
):

    st.markdown(
        "## 🔧 Local Tool"
    )

    tool_name = st.session_state.tool_name

    # --------------------------------------------------------
    # CALCULATOR
    # --------------------------------------------------------

    if tool_name == "Calculator":

        tool_argument = st.text_input(
            "Enter calculation:",
            placeholder="Example: 25 * (10 + 5)",
            key="calculator_input",
        )

    # --------------------------------------------------------
    # FILE INFORMATION
    # --------------------------------------------------------

    elif tool_name == "File Information":

        tool_argument = st.text_input(
            "Enter file or folder path:",
            placeholder=(
                r"Example: C:\Users\YourName\Desktop"
            ),
            key="file_input",
        )

    # --------------------------------------------------------
    # OTHER TOOLS
    # --------------------------------------------------------

    else:

        tool_argument = ""

    # --------------------------------------------------------
    # RUN TOOL
    # --------------------------------------------------------

    if st.button(
        "🔧 Run Tool",
        type="primary",
        use_container_width=True,
        key="run_local_tool_button",
    ):

        with st.spinner(
            "Running local tool..."
        ):

            try:

                result = run_local_tool(
                    tool_name,
                    tool_argument,
                )

                st.session_state.tool_result = result

            except Exception as error:

                st.session_state.tool_result = ""

                st.error(
                    "Tool failed."
                )

                st.caption(
                    str(error)
                )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    if st.session_state.tool_result:

        st.divider()

        st.markdown(
            "### 🔧 Tool Result"
        )

        st.markdown(
            st.session_state.tool_result
        )

    # --------------------------------------------------------
    # CLOSE TOOL
    # --------------------------------------------------------

    if st.button(
        "✕ Close Tool",
        use_container_width=True,
        key="close_tool_button",
    ):

        st.session_state.tool_active = False

        st.session_state.tool_name = ""

        st.session_state.tool_result = ""

        st.rerun()


# ============================================================
# STUDY RESULT
# ============================================================

if (
    st.session_state.mode == "Study"
    and st.session_state.study_result
):

    st.markdown(
        "## 📚 Study Result"
    )

    st.markdown(
        st.session_state.study_result
    )

    st.divider()


# ============================================================
# CODING ASSISTANT
# ============================================================

if st.session_state.mode == "Coding":

    st.markdown(
        "## 💻 Coding Assistant"
    )

    st.caption(
        "Local programming assistant powered by "
        "Llama 3.2 3B."
    )

    coding_input = st.text_area(
        "Enter your code or programming problem:",
        height=250,
        placeholder=(
            "Example:\n\n"
            "Write a Python program to find the "
            "second largest number in a list."
        ),
        key="coding_input",
    )

    if st.button(
        "💻 Run Coding Assistant",
        type="primary",
        use_container_width=True,
        key="run_coding_button",
    ):

        if not coding_input.strip():

            st.warning(
                "Please enter some code or a "
                "programming problem first."
            )

        else:

            with st.spinner(
                "JARVIS is analyzing your code..."
            ):

                try:

                    coding_result = run_coding_action(
                        st.session_state.coding_action,
                        coding_input,
                        st.session_state.coding_language,
                    )

                    st.session_state.coding_result = (
                        coding_result
                    )

                except Exception as error:

                    st.session_state.coding_result = ""

                    st.error(
                        "Coding assistant failed."
                    )

                    st.caption(
                        str(error)
                    )


# ============================================================
# CODING RESULT
# ============================================================

if (
    st.session_state.mode == "Coding"
    and st.session_state.coding_result
):

    st.divider()

    st.markdown(
        "## 💻 Coding Result"
    )

    st.markdown(
        st.session_state.coding_result
    )


# ============================================================
# DOCUMENT STATUS
# ============================================================

if st.session_state.document_text:

    st.info(
        f"📄 JARVIS is using: "
        f"**{st.session_state.document_name}**"
    )


# ============================================================
# WELCOME SCREEN
# ============================================================

if (
    not st.session_state.messages
    and st.session_state.mode != "Coding"
):

    st.markdown(
        "### Hello! 👋"
    )

    st.write(
        "I'm JARVIS, your offline AI assistant. "
        "I can help with studying, programming, "
        "general questions and your documents."
    )

    st.info(
        "Everything runs locally through Ollama."
    )


# ============================================================
# NORMAL CHAT
# ============================================================

if st.session_state.mode != "Coding":

    # --------------------------------------------------------
    # DISPLAY MESSAGES
    # --------------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    # --------------------------------------------------------
    # CHAT INPUT
    # --------------------------------------------------------

    user_input = st.chat_input(
        "Ask JARVIS anything..."
    )

    if user_input:

        # ====================================================
        # MEMORY COMMAND
        # ====================================================

        handled, memory_response = handle_memory_command(
            user_input
        )

        if handled:

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_input,
                }
            )

            save_message(
                st.session_state.session_id,
                "user",
                user_input,
            )

            with st.chat_message(
                "user"
            ):

                st.markdown(
                    user_input
                )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": memory_response,
                }
            )

            save_message(
                st.session_state.session_id,
                "assistant",
                memory_response,
            )

            with st.chat_message(
                "assistant"
            ):

                st.markdown(
                    memory_response
                )

        # ====================================================
        # NORMAL AI
        # ====================================================

        else:

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_input,
                }
            )

            save_message(
                st.session_state.session_id,
                "user",
                user_input,
            )

            with st.chat_message(
                "user"
            ):

                st.markdown(
                    user_input
                )

            # ------------------------------------------------
            # DOCUMENT RETRIEVAL
            # ------------------------------------------------

            document_context = get_document_context(
                user_input,
                st.session_state.document_text,
            )

            # ------------------------------------------------
            # SMART MEMORY
            # ------------------------------------------------

            memories = get_relevant_memories(
                user_input,
                limit=5,
            )

            # ------------------------------------------------
            # ASK JARVIS
            # ------------------------------------------------

            with st.chat_message(
                "assistant"
            ):

                with st.spinner(
                    "JARVIS is thinking..."
                ):

                    try:

                        answer = ask_jarvis(
                            st.session_state.messages,
                            mode=st.session_state.mode,
                            document_context=document_context,
                            memories=memories,
                        )

                        st.markdown(
                            answer
                        )

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer,
                            }
                        )

                        save_message(
                            st.session_state.session_id,
                            "assistant",
                            answer,
                        )

                        # ------------------------------------
                        # AUTO CHAT TITLE
                        # ------------------------------------

                        if len(
                            st.session_state.messages
                        ) == 2:

                            title = user_input[:40]

                            if len(
                                user_input
                            ) > 40:

                                title += "..."

                            update_conversation_title(
                                st.session_state.session_id,
                                title,
                            )

                    except Exception as error:

                        st.error(
                            "Could not connect to Ollama."
                        )

                        st.caption(
                            str(error)
                        )