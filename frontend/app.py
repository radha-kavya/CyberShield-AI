
import streamlit as st
import requests
import uuid


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="CyberShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://127.0.0.1:8000"


# ==================================================
# 2. COLOUR PALETTE
# ==================================================

COLORS = {
    "background": "#FFFFFF",
    "sidebar": "#FCE4E4",
    "cards": "#FFF1F1",
    "heading": "#8F3038",
    "button": "#D96B72",
    "button_text": "#FFFFFF",
    "text": "#292929",
    "secondary_text": "#666666",
    "border": "#E8C5C7",
    "chat_input": "#FFFFFF",
    "chat_text": "#292929"
}


# ==================================================
# 3. SESSION STATE
# ==================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

if "last_retrieved" not in st.session_state:
    st.session_state.last_retrieved = 0


# ==================================================
# 4. CUSTOM THEME
# ==================================================

st.markdown(f"""
<style>

/* Main background */

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main,
.block-container {{
    background-color: {COLORS["background"]} !important;
    color: {COLORS["text"]} !important;
}}

.block-container {{
    max-width: 1300px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}}

/* Main text */

.stApp p,
.stApp label,
.stApp li,
.stApp .stMarkdown {{
    color: {COLORS["text"]};
}}

/* Sidebar */

[data-testid="stSidebar"] {{
    background-color: {COLORS["sidebar"]} !important;
    border-right: 1px solid #F2C5C5;
}}

[data-testid="stSidebar"] * {{
    color: {COLORS["text"]} !important;
}}

[data-testid="stSidebar"] hr {{
    border-color: #EABBBB;
}}

/* Headings */

h1, h2, h3, h4 {{
    color: {COLORS["heading"]} !important;
    font-weight: 800 !important;
}}

/* Captions */

.stCaption,
[data-testid="stCaptionContainer"] {{
    color: {COLORS["secondary_text"]} !important;
}}

/* Metric cards */

[data-testid="stMetric"] {{
    background-color: {COLORS["cards"]} !important;
    border: 1px solid #F1CACA;
    border-left: 5px solid {COLORS["button"]};
    border-radius: 12px;
    padding: 18px;
    box-shadow: 0 3px 12px rgba(143,48,56,0.05);
}}

[data-testid="stMetricLabel"] {{
    color: #494949 !important;
    font-weight: 700;
}}

[data-testid="stMetricValue"] {{
    color: {COLORS["heading"]} !important;
    font-weight: 800;
}}

/* Buttons */

.stButton > button {{
    background-color: {COLORS["button"]} !important;
    color: {COLORS["button_text"]} !important;
    border: 1px solid {COLORS["button"]} !important;
    border-radius: 10px;
    min-height: 45px;
    font-weight: 700;
    transition: 0.2s ease;
}}

.stButton > button p {{
    color: {COLORS["button_text"]} !important;
}}

.stButton > button:hover {{
    background-color: {COLORS["heading"]} !important;
    border-color: {COLORS["heading"]} !important;
}}

.stButton > button:hover p {{
    color: #FFFFFF !important;
}}

/* Chat messages */

[data-testid="stChatMessage"] {{
    background-color: #FFFFFF !important;
    border: 1px solid {COLORS["border"]};
    border-radius: 14px;
    padding: 15px;
    margin-bottom: 12px;
}}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li {{
    color: {COLORS["text"]} !important;
}}

/* Bottom chat input */

[data-testid="stChatInput"] {{
    background-color: {COLORS["chat_input"]} !important;
    border: 2px solid #DDA5A9 !important;
    border-radius: 14px !important;
    opacity: 1 !important;
}}

/* Typed text */

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInput"] [data-baseweb="textarea"] textarea {{
    color: {COLORS["chat_text"]} !important;
    -webkit-text-fill-color: {COLORS["chat_text"]} !important;
    caret-color: {COLORS["chat_text"]} !important;
    background-color: #FFFFFF !important;
    opacity: 1 !important;
    font-size: 16px !important;
}}

/* Placeholder */

[data-testid="stChatInput"] textarea::placeholder {{
    color: {COLORS["secondary_text"]} !important;
    -webkit-text-fill-color: {COLORS["secondary_text"]} !important;
    opacity: 1 !important;
}}

/* Send button */

[data-testid="stChatInput"] button {{
    color: {COLORS["heading"]} !important;
    background-color: #FFFFFF !important;
}}

[data-testid="stChatInput"] button svg {{
    color: {COLORS["heading"]} !important;
    fill: {COLORS["heading"]} !important;
}}

/* Chat input focus */

[data-testid="stChatInput"]:focus-within {{
    border-color: {COLORS["button"]} !important;
    box-shadow: 0 0 0 2px rgba(217,107,114,0.15) !important;
}}

/* Other input fields */

.stTextInput input,
.stTextArea textarea {{
    color: {COLORS["text"]} !important;
    background-color: #FFFFFF !important;
}}

/* Select boxes */

.stSelectbox div[data-baseweb="select"] {{
    background-color: #FFFFFF !important;
}}

[data-baseweb="select"] *,
[data-baseweb="popover"] *,
[role="option"] {{
    color: {COLORS["text"]} !important;
}}

/* Dividers */

hr {{
    border-color: {COLORS["border"]} !important;
}}

/* Links */

a {{
    color: {COLORS["heading"]} !important;
}}

/* Alerts */

[data-testid="stAlert"] {{
    border-radius: 10px;
}}

/* Sidebar buttons */

[data-testid="stSidebar"] .stButton > button {{
    background-color: #FFFFFF !important;
    color: {COLORS["heading"]} !important;
    border: 1px solid #D98B91 !important;
}}

[data-testid="stSidebar"] .stButton > button p {{
    color: {COLORS["heading"]} !important;
}}

[data-testid="stSidebar"] .stButton > button:hover {{
    background-color: {COLORS["button"]} !important;
}}

[data-testid="stSidebar"] .stButton > button:hover p {{
    color: #FFFFFF !important;
}}

</style>
""", unsafe_allow_html=True)


# ==================================================
# 5. BACKEND CONNECTION
# ==================================================

backend_status = "Disconnected"

try:

    health_response = requests.get(
        f"{API_URL}/health",
        timeout=5
    )

    if health_response.status_code == 200:

        backend_status = health_response.json().get(
            "status",
            "unknown"
        )

except requests.exceptions.RequestException:

    backend_status = "Disconnected"


# ==================================================
# 6. SIDEBAR
# ==================================================

with st.sidebar:

    st.title("🛡️ CyberShield AI")

    st.caption("CYBERSECURITY INTELLIGENCE PLATFORM")

    st.divider()

    st.subheader("System Status")

    if backend_status == "healthy":

        st.success("Backend Online")

    elif backend_status == "initializing":

        st.warning("Backend Initializing")

    else:

        st.error("Backend Offline")

    st.caption("API: 127.0.0.1:8000")

    st.divider()

    st.subheader("Investigation Session")

    st.caption(
        f"Session ID: {st.session_state.session_id[:12]}"
    )

    total_questions = sum(
        1
        for message in st.session_state.messages
        if message["role"] == "user"
    )

    st.metric(
        "Questions Asked",
        total_questions
    )

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.session_state.session_id = str(uuid.uuid4())

        st.session_state.last_retrieved = 0

        st.rerun()

    st.divider()

    st.subheader("Platform Features")

    st.markdown("""
    - Multi-format document ingestion
    - Hybrid search
    - Cross-encoder reranking
    - Conversational RAG
    - Local LLM inference
    - Evidence-based answers
    """)

    st.divider()

    st.caption("Built with Python and Generative AI")


# ==================================================
# 7. MAIN HEADER
# ==================================================

st.title("🛡️ CyberShield AI")

st.subheader("Intelligent Cybersecurity Threat Investigation")

st.write(
    "Analyze security incidents, investigate suspicious activity "
    "and retrieve evidence from cybersecurity documents."
)


# ==================================================
# 8. DASHBOARD METRICS
# ==================================================

total_questions = sum(
    1
    for message in st.session_state.messages
    if message["role"] == "user"
)

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "System Status",
        "Online" if backend_status == "healthy" else "Offline"
    )

with col2:

    st.metric(
        "Total Questions",
        total_questions
    )

with col3:

    st.metric(
        "Last Retrieved Documents",
        st.session_state.last_retrieved
    )


st.divider()


# ==================================================
# 9. INVESTIGATION CENTER
# ==================================================

st.subheader("🛡️ Security Investigation Center")

st.write(
    "Use the investigation shortcuts or ask your own "
    "cybersecurity question below."
)


# ==================================================
# 10. QUICK INVESTIGATION
# ==================================================

st.subheader("⚡ Quick Investigation")

prompt_col1, prompt_col2 = st.columns(2)

with prompt_col1:

    if st.button(
        "🔍 Investigate Suspicious IP",
        use_container_width=True
    ):

        st.session_state.pending_question = (
            "Why is IP 198.51.100.23 suspicious?"
        )

        st.rerun()

    if st.button(
        "👤 Identify Targeted Account",
        use_container_width=True
    ):

        st.session_state.pending_question = (
            "Which account did IP 198.51.100.23 target?"
        )

        st.rerun()


with prompt_col2:

    if st.button(
        "🌐 Analyze Network Event",
        use_container_width=True
    ):

        st.session_state.pending_question = (
            "Explain network event NET001."
        )

        st.rerun()

    if st.button(
        "📋 Explain Security Policy",
        use_container_width=True
    ):

        st.session_state.pending_question = (
            "What does the security policy say about suspicious activity?"
        )

        st.rerun()


st.divider()


# ==================================================
# 11. CHAT INTERFACE
# ==================================================

st.subheader("💬 AI Investigation Assistant")

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ==================================================
# 12. CHAT INPUT
# ==================================================

question = st.chat_input(
    "Ask about an IP address, account, incident or network event..."
)


if st.session_state.pending_question:

    question = st.session_state.pending_question

    st.session_state.pending_question = None


# ==================================================
# 13. PROCESS QUESTION
# ==================================================

if question:

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):

        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner(
            "🔎 Investigating security evidence..."
        ):

            try:

                payload = {
                    "question": question,
                    "session_id": st.session_state.session_id
                }

                response = requests.post(
                    f"{API_URL}/ask",
                    json=payload,
                    timeout=300
                )

                response.raise_for_status()

                result = response.json()

                answer = result["answer"]

                retrieved_count = result.get(
                    "retrieved_documents",
                    0
                )

                st.markdown(answer)

                st.caption(
                    f"📚 Retrieved documents: {retrieved_count}"
                )

                st.session_state.last_retrieved = (
                    retrieved_count
                )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except requests.exceptions.RequestException as error:

                st.error(
                    "Unable to connect to CyberShield AI backend."
                )

                st.caption(str(error))

            except Exception as error:

                st.error(
                    "Something went wrong while generating the answer."
                )

                st.caption(str(error))


# ==================================================
# 14. FOOTER
# ==================================================

st.divider()

st.caption(
    "🛡️ CyberShield AI | Python · Streamlit · FastAPI · "
    "LangChain · ChromaDB · Ollama"
)
