import streamlit as st
import os

st.set_page_config(
    page_title="SupplyShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from dashboard import overview, graph_page, recall_page, explorer, metrics, risk_analysis, temperature
from graph.graph_builder import build_supply_chain_graph
if "G" not in st.session_state:
    st.session_state.G = build_supply_chain_graph()

# ── Page registry ──────────────────────────────────────────────────────────────
PAGES = {
    "Overview":       overview.render,
    "Risk Analysis":  risk_analysis.render,
    "Chain Explorer": explorer.render,
    "Graph View":     graph_page.render,
    "Recall Center":  recall_page.render,
    "Cold Chain":     temperature.render,
    "Metrics":        metrics.render,
}

# Visual group labels shown above nav items (purely decorative markdown)
NAV_GROUPS = {
    "Intelligence": ["Overview", "Risk Analysis"],
    "Explore":      ["Chain Explorer", "Graph View"],
    "Operations":   ["Recall Center", "Cold Chain", "Metrics"],
}

# Flat ordered list for the single radio widget
_NAV_ORDER = [p for pages in NAV_GROUPS.values() for p in pages]


def load_css() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* ── Tokens ── */
    :root {
        --bg:          #F7F7F5;
        --surface:     #FFFFFF;
        --border:      #E8E8E4;
        --accent:      #8B6FD8;
        --accent-deep: #654A93;
        --safe:        #7FD1C3;
        --warn:        #F4B860;
        --crit:        #F15A29;
        --pink:        #E8B7B0;
        --text-1:      #1F1F1F;
        --text-2:      #6E6E6E;
        --text-3:      #A0A0A0;
        --radius-card: 20px;
        --radius-btn:  14px;
        --shadow-sm:   0 1px 4px rgba(0,0,0,0.06);
        --shadow-md:   0 4px 20px rgba(0,0,0,0.08);
    }

    /* ── Global reset ── */
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
        background-color: var(--bg) !important;
        color: var(--text-1) !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    #MainMenu, footer, header { visibility: hidden !important; }
    [data-testid="stDecoration"],
    [data-testid="stToolbar"]  { display: none !important; }

    /* ── Layout ── */
    .block-container {
        padding: 2rem 2.5rem 4rem 2.5rem !important;
        max-width: 1480px !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
        min-width: 240px !important;
        max-width: 240px !important;
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

    /* Hide the radio button circles */
    [data-testid="stSidebar"] .stRadio [role="radio"] { display: none !important; }
    [data-testid="stSidebar"] .stRadio > div         { gap: 0 !important; }
    [data-testid="stSidebar"] .stRadio label {
        border-radius: 10px !important;
        padding: 9px 14px !important;
        margin: 1px 6px !important;
        cursor: pointer !important;
        color: var(--text-2) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        transition: background 0.15s ease, color 0.15s ease !important;
        line-height: 1.4 !important;
        display: block !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(139,111,216,0.08) !important;
        color: var(--accent) !important;
    }
    [data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
        font-size: 0.875rem !important;
        color: inherit !important;
        font-weight: inherit !important;
        margin: 0 !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: var(--accent) !important;
        color: #fff !important;
        border: none !important;
        border-radius: var(--radius-btn) !important;
        padding: 10px 22px !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        transition: background 0.18s, transform 0.12s, box-shadow 0.18s !important;
        box-shadow: 0 2px 8px rgba(139,111,216,0.25) !important;
    }
    .stButton > button:hover {
        background: var(--accent-deep) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(139,111,216,0.35) !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* ── Download button ── */
    [data-testid="stDownloadButton"] > button {
        background: var(--surface) !important;
        color: var(--text-2) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: var(--radius-btn) !important;
        padding: 10px 22px !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        transition: border-color 0.15s, box-shadow 0.15s, transform 0.12s !important;
        box-shadow: var(--shadow-sm) !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px rgba(139,111,216,0.15) !important;
    }

    /* ── Metric cards ── */
    div[data-testid="stMetric"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-card) !important;
        padding: 22px 26px !important;
        box-shadow: var(--shadow-sm) !important;
        transition: box-shadow 0.2s, transform 0.2s !important;
    }
    div[data-testid="stMetric"]:hover {
        box-shadow: var(--shadow-md) !important;
        transform: translateY(-2px) !important;
    }
    div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 2rem !important;
        font-weight: 500 !important;
        color: var(--accent-deep) !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        color: var(--text-3) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
    }

    /* ── DataFrame ── */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* ── Text input ── */
    [data-testid="stTextInput"] input {
        border-radius: 12px !important;
        border: 1.5px solid var(--border) !important;
        background: var(--surface) !important;
        font-size: 0.9rem !important;
        color: var(--text-1) !important;
        padding: 10px 16px !important;
        transition: border-color 0.15s, box-shadow 0.15s !important;
        box-shadow: var(--shadow-sm) !important;
    }
    [data-testid="stTextInput"] input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 4px rgba(139,111,216,0.12) !important;
    }

    /* ── Selectbox ── */
    [data-testid="stSelectbox"] > div > div {
        border-radius: 12px !important;
        border: 1.5px solid var(--border) !important;
        background: var(--surface) !important;
    }

    /* ── Checkbox ── */
    [data-testid="stCheckbox"] label {
        font-size: 0.875rem !important;
        color: var(--text-2) !important;
        font-weight: 500 !important;
    }

    /* ── Alerts ── */
    [data-testid="stAlert"] { border-radius: 14px !important; }

    /* ── Divider ── */
    hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }

    /* ── Page fade-in ── */
    .main .block-container {
        animation: appFadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    @keyframes appFadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    [data-testid="stSpinner"] { color: var(--accent) !important; }

    /* ── Nav group label ── */
    .nav-group-label {
        font-size: 0.6rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.9px;
        color: #A0A0A0;
        padding: 12px 20px 3px 20px;
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)


def _render_sidebar() -> str:
    """Renders sidebar and returns the selected page name."""

    # Brand
    st.markdown("""
    <div style="padding:22px 18px 16px 18px;border-bottom:1px solid #E8E8E4;margin-bottom:6px;">
        <div style="display:flex;align-items:center;gap:11px;">
            <div style="
                width:36px;height:36px;flex-shrink:0;
                background:linear-gradient(135deg,#8B6FD8,#654A93);
                border-radius:11px;
                display:flex;align-items:center;justify-content:center;
                font-size:1rem;
                box-shadow:0 4px 10px rgba(139,111,216,0.3);
            ">🛡️</div>
            <div>
                <div style="font-size:0.95rem;font-weight:700;color:#1F1F1F;letter-spacing:-0.2px;">SupplyShield</div>
                <div style="font-size:0.65rem;color:#A0A0A0;font-weight:400;margin-top:1px;">Food Safety Intelligence</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Single flat radio — simple, reliable, works with all Streamlit versions
    # (Keep label_visible='visible' so the sidebar options are guaranteed to render.)

    selected = st.radio(
        "Navigation",
        options=_NAV_ORDER,
        index=_NAV_ORDER.index(st.session_state.get("_page", "Overview")),
        label_visibility="visible",
        key="_nav_radio",
    )


    # Footer
    st.markdown("""
    <div style="padding:16px 18px 12px 18px;border-top:1px solid #E8E8E4;margin-top:12px;">
        <div style="display:flex;align-items:center;gap:8px;">
            <div style="width:7px;height:7px;border-radius:50%;background:#7FD1C3;
                        box-shadow:0 0 0 2px rgba(127,209,195,0.3);"></div>
            <span style="font-size:0.68rem;color:#A0A0A0;font-weight:500;">System Operational · v1.0</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    return selected


def main() -> None:
    load_css()

    # Init global state
    for key, val in [("recall_issued", False), ("recall_confirmed", False), ("_page", "Overview")]:
        if key not in st.session_state:
            st.session_state[key] = val

    # Build graph once
    if "G" not in st.session_state:
        if not os.path.exists("data/suppliers.csv"):
            st.error("Data files not found. Run `python generate_data.py` first.")
            return
        with st.spinner("Building supply chain graph…"):
            st.session_state.G = build_supply_chain_graph()

    # Sidebar
    with st.sidebar:
        # Debug-friendly: ensure something obvious always renders in the sidebar.
        st.markdown("### Navigation")
        selected_page = _render_sidebar()


    # Track and render selected page
    st.session_state["_page"] = selected_page
    PAGES[selected_page]()


if __name__ == "__main__":
    main()
