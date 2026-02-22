import streamlit as st
from sqlalchemy.engine.url import make_url
import re
import base64
import os
from sqlalchemy import create_engine, exc

# ─────────────────────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NaturalDB",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# Premium Dark Theme — Custom CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Root Variables ────────────────────────────── */
    :root {
        --bg-primary: #0a0e1a;
        --bg-secondary: #111827;
        --bg-card: rgba(17, 24, 39, 0.7);
        --bg-glass: rgba(255, 255, 255, 0.03);
        --border-glass: rgba(255, 255, 255, 0.08);
        --border-glow: rgba(99, 102, 241, 0.3);
        --accent-1: #6366f1;
        --accent-2: #8b5cf6;
        --accent-3: #a78bfa;
        --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a78bfa 100%);
        --accent-gradient-hover: linear-gradient(135deg, #818cf8 0%, #a78bfa 50%, #c4b5fd 100%);
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --success: #34d399;
        --error: #f87171;
        --warning: #fbbf24;
        --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        --font-display: 'Outfit', 'Inter', sans-serif;
        --font-mono: 'JetBrains Mono', monospace;
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 8px 32px rgba(0, 0, 0, 0.4);
        --shadow-glow: 0 0 30px rgba(99, 102, 241, 0.15);
    }

    /* ── Base / Page ───────────────────────────────── */
    .stApp {
        background: var(--bg-primary) !important;
        font-family: var(--font-sans) !important;
        color: var(--text-primary) !important;
    }
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background:
            radial-gradient(ellipse 80% 60% at 10% 20%, rgba(99,102,241,0.08), transparent),
            radial-gradient(ellipse 60% 50% at 90% 80%, rgba(139,92,246,0.06), transparent);
        pointer-events: none;
        z-index: 0;
    }
    .main .block-container {
        max-width: 900px;
        padding: 2rem 1.5rem 4rem;
    }

    /* ── Sidebar ───────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1629 0%, #111827 100%) !important;
        border-right: 1px solid var(--border-glass) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        font-family: var(--font-sans) !important;
        color: var(--text-secondary) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    /* ── Headers ───────────────────────────────────── */
    h1, h2, h3 {
        font-family: var(--font-display) !important;
        color: var(--text-primary) !important;
    }
    h1 { font-weight: 800 !important; letter-spacing: -0.03em; }

    /* ── Buttons ───────────────────────────────────── */
    .stButton > button,
    button[kind="primary"],
    .stFormSubmitButton > button {
        background: var(--accent-gradient) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        font-family: var(--font-sans) !important;
        font-weight: 600 !important;
        padding: 0.65rem 1.5rem !important;
        letter-spacing: 0.01em;
        transition: all 0.3s cubic-bezier(.4,0,.2,1) !important;
        box-shadow: 0 4px 16px rgba(99,102,241,0.25) !important;
    }
    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: var(--accent-gradient-hover) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(99,102,241,0.35) !important;
    }
    .stButton > button:active,
    .stFormSubmitButton > button:active {
        transform: translateY(0) !important;
    }

    /* ── Inputs ────────────────────────────────────── */
    .stTextInput input,
    .stNumberInput input,
    .stSelectbox > div > div {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
        font-family: var(--font-sans) !important;
        transition: border-color 0.25s ease !important;
    }
    .stTextInput input:focus,
    .stNumberInput input:focus {
        border-color: var(--accent-1) !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    }

    /* ── Forms ─────────────────────────────────────── */
    [data-testid="stForm"] {
        background: var(--bg-card) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        box-shadow: var(--shadow-md), var(--shadow-glow) !important;
    }

    /* ── Chat Input ────────────────────────────────── */
    .stChatInput textarea,
    div[data-testid="stChatInput"] textarea {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 14px !important;
        color: var(--text-primary) !important;
        font-family: var(--font-sans) !important;
    }
    .stChatInput textarea:focus,
    div[data-testid="stChatInput"] textarea:focus {
        border-color: var(--accent-1) !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    }

    /* ── Toasts & Alerts ───────────────────────────── */
    .stAlert, div[data-testid="stToast"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
    }

    /* ── Chat Messages ─────────────────────────────── */
    div[data-testid="stChatMessage"] {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 16px !important;
        padding: 1rem 1.25rem !important;
        margin-bottom: 0.75rem !important;
        backdrop-filter: blur(8px) !important;
        animation: msgFadeIn 0.4s ease-out;
    }
    @keyframes msgFadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Spinner ────────────────────────────────────── */
    .stSpinner > div {
        border-top-color: var(--accent-1) !important;
    }

    /* ── Dividers ───────────────────────────────────── */
    hr {
        border-color: var(--border-glass) !important;
    }

    /* ── Scrollbar ──────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(99,102,241,0.3);
        border-radius: 3px;
    }

    /* ── Hero Header ────────────────────────────────── */
    .hero-container {
        text-align: center;
        padding: 2.5rem 1rem 1.5rem;
        margin-bottom: 1.5rem;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(99,102,241,0.15);
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 100px;
        padding: 0.35rem 1rem;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--accent-3);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 1rem;
        font-family: var(--font-sans);
    }
    .hero-title {
        font-family: var(--font-display);
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.1;
        margin: 0 0 0.75rem;
        background: linear-gradient(135deg, #f1f5f9 0%, #c4b5fd 40%, #818cf8 70%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .hero-subtitle {
        font-family: var(--font-sans);
        font-size: 1.05rem;
        font-weight: 400;
        color: var(--text-secondary);
        max-width: 500px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ── Status Pill ────────────────────────────────── */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 0.3rem 0.85rem;
        border-radius: 100px;
        font-size: 0.78rem;
        font-weight: 600;
        font-family: var(--font-sans);
        letter-spacing: 0.02em;
    }
    .status-connected {
        background: rgba(52,211,153,0.12);
        border: 1px solid rgba(52,211,153,0.25);
        color: var(--success);
    }
    .status-disconnected {
        background: rgba(248,113,113,0.10);
        border: 1px solid rgba(248,113,113,0.20);
        color: var(--error);
    }
    .pulse-dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
    }
    .pulse-dot.green { background: var(--success); }
    .pulse-dot.red   { background: var(--error); }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%      { opacity: 0.5; transform: scale(0.85); }
    }

    /* ── Sidebar Brand ──────────────────────────────── */
    .sidebar-brand {
        text-align: center;
        padding: 1.25rem 0 1rem;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid var(--border-glass);
    }
    .sidebar-brand-name {
        font-family: var(--font-display);
        font-size: 1.35rem;
        font-weight: 700;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .sidebar-brand-tag {
        font-family: var(--font-sans);
        font-size: 0.7rem;
        color: var(--text-muted);
        margin-top: 2px;
        letter-spacing: 0.04em;
    }

    /* ─ Guide card ──────────────────────────────────── */
    .guide-card {
        background: var(--bg-glass);
        border: 1px solid var(--border-glass);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        margin-top: 1rem;
    }
    .guide-card h4 {
        font-family: var(--font-display) !important;
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-primary) !important;
        margin: 0 0 0.6rem;
    }
    .guide-card ol {
        padding-left: 1.2rem;
        margin: 0;
    }
    .guide-card li {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-bottom: 0.35rem;
        line-height: 1.5;
    }

    /* ── Feature chips ──────────────────────────────── */
    .feature-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: center;
        margin-top: 1.25rem;
    }
    .chip {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: var(--bg-glass);
        border: 1px solid var(--border-glass);
        border-radius: 100px;
        padding: 0.35rem 0.85rem;
        font-size: 0.78rem;
        font-weight: 500;
        color: var(--text-secondary);
        font-family: var(--font-sans);
        transition: all 0.25s ease;
    }
    .chip:hover {
        border-color: var(--border-glow);
        color: var(--accent-3);
        background: rgba(99,102,241,0.06);
    }

    /* ── Welcome card ───────────────────────────────── */
    .welcome-card {
        background: var(--bg-card);
        border: 1px solid var(--border-glass);
        border-radius: 18px;
        padding: 2rem;
        text-align: center;
        box-shadow: var(--shadow-md);
        margin-bottom: 1.5rem;
        backdrop-filter: blur(8px);
    }
    .welcome-card h3 {
        font-family: var(--font-display) !important;
        font-size: 1.3rem;
        margin-bottom: 0.5rem;
    }
    .welcome-card p {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }

    /* ── Hide default streamlit elements ────────────── */
    #MainMenu { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent !important; }
    footer { visibility: hidden; }
    .stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Database Configuration
# ─────────────────────────────────────────────────────────────
DB_CONFIG = {
    "MySQL":      {"port": 3306, "prefix": "mysql"},
    "PostgreSQL": {"port": 5432, "prefix": "postgresql"},
    "SQLite":     {"port": None, "prefix": "sqlite"},
}


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        "connected": False,
        "past": [],
        "generated": [],
        "db_uri": "",
        "db_type": "",
        "processing": False,
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def validate_db_connection(db_uri: str, db_type: str, schema: str):
    """Test that the database is actually reachable."""
    try:
        if db_type == "SQLite" and not os.path.exists(schema):
            raise ValueError(f"Database file '{schema}' not found")
        engine = create_engine(db_uri)
        with engine.connect():
            pass
        return True
    except exc.SQLAlchemyError as e:
        raise ValueError(f"Connection failed: {e}") from e


def process_mermaid_content(content: str):
    """Extract mermaid code blocks → image URLs; return (cleaned_text, urls)."""
    urls: list[str] = []

    def _replace(match):
        code = match.group(1).strip()
        encoded = base64.urlsafe_b64encode(code.encode()).decode()
        urls.append(f"https://mermaid.ink/svg/{encoded}")
        return ""

    text = re.sub(r"```mermaid(.*?)```", _replace, content, flags=re.DOTALL).strip()
    return text, urls


# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Brand
        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-brand-name">🧬 NaturalDB</div>
            <div class="sidebar-brand-tag">Natural-Language Database Interface</div>
        </div>
        """, unsafe_allow_html=True)

        # Status pill
        if st.session_state.get("connected"):
            db = st.session_state.get("db_type", "")
            st.markdown(f"""
            <div style="text-align:center;margin:.75rem 0;">
                <span class="status-pill status-connected">
                    <span class="pulse-dot green"></span> Connected — {db}
                </span>
            </div>
            """, unsafe_allow_html=True)

            if st.button("⏏  Disconnect", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        else:
            st.markdown("""
            <div style="text-align:center;margin:.75rem 0;">
                <span class="status-pill status-disconnected">
                    <span class="pulse-dot red"></span> Not Connected
                </span>
            </div>
            """, unsafe_allow_html=True)

        # Guide
        st.markdown("""
        <div class="guide-card">
            <h4>📖 Quick Guide</h4>
            <ol>
                <li>Select your database type & connect</li>
                <li>Ask questions in plain English</li>
                <li>Get instant results, insights & ER diagrams</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.caption("Built with CrewAI · Streamlit · Gemini")


# ─────────────────────────────────────────────────────────────
# Connection Form
# ─────────────────────────────────────────────────────────────
def database_connection_form():
    # Hero
    st.markdown("""
    <div class="hero-container">
        <div class="hero-badge">AI-Powered Database Assistant</div>
        <div class="hero-title">NaturalDB</div>
        <div class="hero-subtitle">
            Talk to any relational database in plain English.
            Perform queries, analysis, CRUD operations and generate ER diagrams — effortlessly.
        </div>
        <div class="feature-chips">
            <span class="chip">💬 Natural Language</span>
            <span class="chip">📊 Data Analysis</span>
            <span class="chip">🛠️ CRUD Ops</span>
            <span class="chip">🧩 ER Diagrams</span>
            <span class="chip">🔒 Secure</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("db_connection"):
        st.subheader("🔗 Connect Your Database")

        db_type = st.selectbox(
            "Database Engine",
            list(DB_CONFIG.keys()),
            help="Choose the RDBMS you want to query",
        )

        if db_type == "SQLite":
            st.caption("Enter the path to your `.db` file  (e.g. `data/chinook.db`)")
        else:
            st.caption("Provide your database server credentials below")

        schema_label = "📁 Database Path" if db_type == "SQLite" else "📚 Database Name"
        schema = st.text_input(
            schema_label,
            placeholder="my_database.db" if db_type == "SQLite" else "my_database",
        )

        if db_type != "SQLite":
            st.markdown("---")
            col_host, col_port = st.columns(2)
            with col_host:
                host_input = st.text_input("🌐 Host", value="localhost")
            with col_port:
                port_input = st.number_input(
                    "🔌 Port", value=DB_CONFIG[db_type]["port"]
                )
            col_user, col_pass = st.columns(2)
            with col_user:
                username = st.text_input("👤 Username")
            with col_pass:
                password = st.text_input("🔑 Password", type="password")

        submitted = st.form_submit_button("Connect →", use_container_width=True)

        if submitted:
            try:
                if db_type == "SQLite":
                    db_uri = f"{DB_CONFIG[db_type]['prefix']}:///{schema}"
                else:
                    db_uri = (
                        f"{DB_CONFIG[db_type]['prefix']}://"
                        f"{username}:{password}@{host_input}:{port_input}/{schema}"
                    )

                with st.spinner("Testing connection …"):
                    make_url(db_uri)
                    validate_db_connection(db_uri, db_type, schema)

                st.session_state.update(
                    {"connected": True, "db_uri": db_uri, "db_type": db_type}
                )
                st.toast("✅ Connected!", icon="🎉")

            except Exception as e:
                st.session_state.connected = False
                st.error(f"**Connection failed:** {e}")
                st.stop()


# ─────────────────────────────────────────────────────────────
# Query Processing
# ─────────────────────────────────────────────────────────────
def handle_query_processing():
    try:
        from src.crew import SolveUserQueryCrew

        crew = SolveUserQueryCrew().solve_query_crew()
        result = crew.kickoff(
            inputs={
                "db_uri": st.session_state.db_uri,
                "query": st.session_state.past[-1],
                "database": st.session_state.db_type.lower(),
            }
        )
        response = str(getattr(result, "result", str(result)))
        if not response:
            return "Received empty response from the query processor.", []
        return process_mermaid_content(response)
    except Exception as e:
        return f"🚨 **Error processing query**\n\n{e}", []


# ─────────────────────────────────────────────────────────────
# Chat Interface
# ─────────────────────────────────────────────────────────────
def chat_interface():
    db = st.session_state.db_type
    st.markdown(f"""
    <div class="hero-container" style="padding:1.5rem 1rem 0.75rem;">
        <div class="hero-badge">Connected to {db}</div>
        <div class="hero-title" style="font-size:2rem;">Ask anything about your data</div>
        <div class="hero-subtitle" style="font-size:0.92rem;">
            Type a question below — NaturalDB will analyze, query, and respond in real time.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Welcome card on first load
    if not st.session_state.generated:
        st.markdown("""
        <div class="welcome-card">
            <h3>👋 Welcome!</h3>
            <p>Your AI database assistant is ready. Here are some things you can try:</p>
            <div class="feature-chips" style="justify-content:center;">
                <span class="chip">💬 "Show me all users"</span>
                <span class="chip">📊 "Analyze sales trends"</span>
                <span class="chip">🧩 "Generate ER diagram"</span>
                <span class="chip">🛠️ "Create a new table"</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Display chat history using Streamlit's native chat_message
    for i in range(len(st.session_state.past)):
        with st.chat_message("user", avatar="👤"):
            st.markdown(st.session_state.past[i])

        if i < len(st.session_state.generated):
            text_content, image_urls = st.session_state.generated[i]
            with st.chat_message("assistant", avatar="🧬"):
                if text_content:
                    st.markdown(text_content)
                if image_urls:
                    for idx, url in enumerate(image_urls):
                        st.image(url, use_container_width=True, caption=f"Diagram {idx + 1}")

    # Chat input
    if st.session_state.connected and not st.session_state.processing:
        query = st.chat_input("Ask your database something …")
        if query:
            st.session_state.past.append(query)
            st.session_state.processing = True
            st.rerun()

    # Process pending query
    if st.session_state.processing:
        with st.chat_message("assistant", avatar="🧬"):
            with st.spinner("🔍 Analyzing your query …"):
                text_response, image_urls = handle_query_processing()
                st.session_state.generated.append((text_response, image_urls))
                st.session_state.processing = False
                st.rerun()


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
def main():
    init_session_state()
    render_sidebar()

    if not st.session_state.connected:
        database_connection_form()
    else:
        chat_interface()


if __name__ == "__main__":
    main()