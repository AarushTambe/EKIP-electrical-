import streamlit as st

from rag.rag_engine import ElectricalRAG
from voice.voice_engine import listen, speak


# ============================================================
# CONFIGURATION
# ============================================================

INDEX_PATH = "knowledge/index/Theraja_V2.faiss"
METADATA_PATH = "knowledge/index/Theraja_V2.json"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="EKIP",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- App ---------- */

    .stApp {
        background: #0f1117;
    }

    .main .block-container {
        max-width: 1100px;
        padding-top: 1rem;
        padding-bottom: 0.5rem;
    }


    /* ---------- Sidebar ---------- */

    section[data-testid="stSidebar"] {
        background: #14171f;
        border-right: 1px solid #252934;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 0.8rem;
        padding-left: 0.8rem;
        padding-right: 0.8rem;
    }


    /* ---------- Text ---------- */

    h1, h2, h3 {
        color: #f1f3f6 !important;
    }

    [data-testid="stCaptionContainer"] {
        color: #8d95a3;
    }


    /* ---------- Buttons ---------- */

    .stButton > button {
        background: #191d26;
        border: 1px solid #292e38;
        color: #dce0e6;
        border-radius: 9px;
        min-height: 2.2rem;
    }

    .stButton > button:hover {
        background: #202531;
        border-color: #3b4250;
        color: white;
    }


    /* ---------- Chat messages ---------- */

    [data-testid="stChatMessage"] {
        border-radius: 12px;
    }


    /* ---------- Chat input ---------- */

    [data-testid="stChatInput"] {
        background: #171b23;
        border: 1px solid #2b303a;
        border-radius: 13px;
    }


    /* ---------- Expander ---------- */

    [data-testid="stExpander"] {
        background: #151920;
        border: 1px solid #272c35;
        border-radius: 9px;
    }


    /* ---------- Reduce spacing ---------- */

    div[data-testid="stVerticalBlock"] {
        gap: 0.55rem;
    }


    /* ---------- Hide Streamlit extras ---------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD RAG
# ============================================================

@st.cache_resource
def load_rag():

    rag = ElectricalRAG()

    if not rag.load_index(
        INDEX_PATH,
        METADATA_PATH,
    ):
        raise FileNotFoundError(
            "Persistent knowledge base was not found."
        )

    return rag


try:

    rag = load_rag()

except Exception as error:

    st.error(
        f"Could not load the knowledge base: {error}"
    )

    st.stop()


# ============================================================
# SESSION STATE
# ============================================================

if "chats" not in st.session_state:

    st.session_state.chats = {
        "chat_1": {
            "title": "New Chat",
            "messages": [],
        }
    }


if "current_chat_id" not in st.session_state:

    st.session_state.current_chat_id = "chat_1"


if "chat_counter" not in st.session_state:

    st.session_state.chat_counter = 1


if "voice_output" not in st.session_state:

    st.session_state.voice_output = False


# ============================================================
# CHAT FUNCTIONS
# ============================================================

def create_new_chat():

    st.session_state.chat_counter += 1

    chat_id = f"chat_{st.session_state.chat_counter}"

    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": [],
    }

    st.session_state.current_chat_id = chat_id


def generate_chat_title(question):

    words = question.strip().split()

    if not words:
        return "New Chat"

    title = " ".join(words[:5])

    if len(words) > 5:
        title += "..."

    return title


def display_sources(sources):

    if not sources:
        return

    unique_sources = []
    seen = set()

    for source in sources:

        key = (
            source["source"],
            source["page"],
        )

        if key not in seen:

            seen.add(key)
            unique_sources.append(source)

    with st.expander(
        f"📚 Sources · {len(unique_sources)}"
    ):

        for source in unique_sources:

            st.caption(
                f"📖 {source['source']} · Page {source['page']}"
            )


# ============================================================
# PROCESS QUESTION
# ============================================================

def process_question(question):

    question = question.strip()

    if not question:
        return

    chat = st.session_state.chats[
        st.session_state.current_chat_id
    ]

    messages = chat["messages"]

    # First question becomes title

    if not messages:

        chat["title"] = generate_chat_title(
            question
        )

    # Store question

    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    # Current chat history only

    history = [
        {
            "role": message["role"],
            "content": message["content"],
        }
        for message in messages[:-1]
    ]

    # Generate answer

    with st.spinner(
        "Searching the textbook..."
    ):

        result = rag.answer(
            question,
            chat_history=history,
        )

    # Store answer

    messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        }
    )

    # Optional voice

    if st.session_state.voice_output:

        speak(result["answer"])

    st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("⚡ EKIP")

    st.caption(
        "Electrical Knowledge & Intelligence Platform"
    )

    if st.button(
        "＋ New chat",
        use_container_width=True,
    ):

        create_new_chat()
        st.rerun()

    st.divider()

    st.caption("CHATS")

    for chat_id, chat in st.session_state.chats.items():

        if chat_id == st.session_state.current_chat_id:

            label = f"● {chat['title']}"

        else:

            label = chat["title"]

        if st.button(
            label,
            key=f"chat_{chat_id}",
            use_container_width=True,
        ):

            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.divider()

    st.caption("KNOWLEDGE BASE")

    st.write("📚 Theraja — Electrical Technology")
    st.caption(
        f"{len(rag.documents):,} indexed chunks"
    )

    st.caption("AI SYSTEM")

    st.write("🧠 Mistral")
    st.write("🔎 FAISS")
    st.write("📖 Source grounded")

    st.caption("VOICE")

    st.session_state.voice_output = st.checkbox(
        "Read answers aloud",
        value=st.session_state.voice_output,
    )


# ============================================================
# CURRENT CHAT
# ============================================================

current_chat = st.session_state.chats[
    st.session_state.current_chat_id
]

messages = current_chat["messages"]


# ============================================================
# MAIN HEADER
# ============================================================

top_left, top_right = st.columns(
    [5, 1]
)

with top_left:

    st.title("⚡ EKIP")

    st.caption(
        "Electrical Engineering Intelligent Tutor"
    )

with top_right:

    st.write("")

    st.caption("● Online")


st.divider()


# ============================================================
# EMPTY CHAT
# ============================================================

if not messages:

    st.write("")

    center_left, center, center_right = st.columns(
        [1, 3, 1]
    )

    with center:

        st.markdown(
            "### Welcome to EKIP"
        )

        st.caption(
            "Your Electrical Engineering AI tutor."
        )

        st.caption(
            "Ask about concepts, machines, transformers, "
            "circuits, or numerical problems."
        )

        st.write("")

        st.info(
            "💡 Try asking:  **What is a DC motor?**"
        )


# ============================================================
# CHAT TITLE
# ============================================================

else:

    st.subheader(
        current_chat["title"]
    )


# ============================================================
# CHAT HISTORY
# ============================================================

for message in messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if message["role"] == "assistant":

            display_sources(
                message.get(
                    "sources",
                    [],
                )
            )


# ============================================================
# VOICE BUTTON
# ============================================================

if messages:

    left, middle, right = st.columns(
        [1, 2, 1]
    )

    with middle:

        if st.button(
            "🎙️ Ask by voice",
            use_container_width=True,
        ):

            with st.spinner(
                "Listening..."
            ):

                voice_question = listen()

            if voice_question:

                process_question(
                    voice_question
                )

            else:

                st.warning(
                    "I couldn't understand the audio."
                )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask an Electrical Engineering question..."
)

if question:

    process_question(
        question
    )