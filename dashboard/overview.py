import streamlit as st
from analytics.contamination_detector import get_contaminated_batches, get_affected_source_nodes
from analytics.risk_scoring import get_recall_efficiency
from graph.traversal import get_blast_radius

_A = "#8B6FD8"; _D = "#654A93"; _S = "#7FD1C3"; _W = "#F4B860"; _C = "#F15A29"; _P = "#E8B7B0"

_PALETTE = {
    "Supplier": _D, "Distribution Center": _A,
    "Kitchen": "#7D6DB7", "Store": _S, "Product": _P,
}


def _kpi(label, value, color, col):
    with col:
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E8E8E4;border-radius:16px;'
            f'padding:20px 22px;border-top:3px solid {color};'
            f'box-shadow:0 1px 4px rgba(0,0,0,0.05);">'
            f'<div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            f'letter-spacing:0.8px;color:#A0A0A0;margin-bottom:8px;">{label}</div>'
            f'<div style="font-family:monospace;font-size:2.2rem;font-weight:600;'
            f'color:{color};letter-spacing:-1px;line-height:1;">{value}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render():
    G = st.session_state.G

    type_counts: dict = {}
    for _, d in G.nodes(data=True):
        t = d.get("type", "Unknown")
        type_counts[t] = type_counts.get(t, 0) + 1

    contaminated_batches = get_contaminated_batches()
    affected_sources = get_affected_source_nodes(G)
    affected_nodes: set = set()
    for src in affected_sources:
        affected_nodes.update(get_blast_radius(G, src).nodes())

    affected_stores   = {n for n in affected_nodes if G.nodes[n].get("type") == "Store"}
    affected_products = {n for n in affected_nodes if G.nodes[n].get("type") == "Product"}
    eff = get_recall_efficiency(G, affected_nodes)

    is_critical = bool(contaminated_batches)
    s_color = _C if is_critical else _S
    s_bg    = "#FEF0EB" if is_critical else "#EBF9F7"
    s_bdr   = "#F9C3B1" if is_critical else "#B2E8E1"
    s_lbl   = "CRITICAL ALERT" if is_critical else "ALL SYSTEMS NOMINAL"

    # ── Header ──────────────────────────────────────────────────────
    col_h, col_s = st.columns([5, 2])
    with col_h:
        st.markdown("## Executive Overview")
        st.caption("Real-time food safety intelligence across the supply chain.")
    with col_s:
        st.markdown(
            f'<div style="display:flex;justify-content:flex-end;padding-top:10px;">'
            f'<span style="display:inline-flex;align-items:center;gap:8px;padding:8px 16px;'
            f'border-radius:999px;border:1.5px solid {s_bdr};background:{s_bg};'
            f'font-size:0.68rem;font-weight:700;color:{s_color};letter-spacing:1.2px;">'
            f'<span style="width:7px;height:7px;border-radius:50%;background:{s_color};'
            f'display:inline-block;"></span>{s_lbl}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── KPI row ─────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    _kpi("Failed Batches",    len(contaminated_batches), _C if contaminated_batches else _S, c1)
    _kpi("Blast Radius",      len(affected_nodes),       _W if affected_nodes else _S,       c2)
    _kpi("Stores Affected",   len(affected_stores),      _C if affected_stores else _S,      c3)
    _kpi("Products Impacted", len(affected_products),    _C if affected_products else _S,    c4)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Recall efficiency ────────────────────────────────────────────
    st.markdown(
        '<p style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.8px;color:#A0A0A0;margin-bottom:10px;">Recall Efficiency</p>',
        unsafe_allow_html=True,
    )
    e1, e2, e3, e4 = st.columns(4)
    with e1: st.metric("Total Network", eff["total_nodes"])
    with e2: st.metric("Targeted Recall", eff["targeted"])
    with e3: st.metric("Nodes Saved", eff["saved"])
    with e4: st.metric("Efficiency", f"{eff['efficiency_pct']}%")

    st.markdown("---")

    # ── Alerts ───────────────────────────────────────────────────────
    if is_critical:
        for batch in contaminated_batches[:5]:
            st.error(
                f"⚠️ **Contamination Detected** — Batch **{batch}** failed pathogen "
                f"screening. **{len(affected_nodes)}** downstream nodes at risk."
            )

    # ── Network composition ──────────────────────────────────────────
    st.markdown(
        '<p style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.8px;color:#A0A0A0;margin-bottom:10px;">Network Composition</p>',
        unsafe_allow_html=True,
    )

    total = sum(type_counts.values()) or 1
    rows_html = ""
    for t, cnt in sorted(type_counts.items(), key=lambda x: -x[1]):
        color = _PALETTE.get(t, "#A0A0A0")
        pct   = round(cnt / total * 100)
        rows_html += (
            f'<div style="display:flex;align-items:center;gap:12px;padding:10px 0;'
            f'border-bottom:1px solid #F7F7F5;">'
            f'<div style="width:10px;height:10px;border-radius:50%;'
            f'background:{color};flex-shrink:0;"></div>'
            f'<span style="flex:1;font-size:0.875rem;font-weight:500;color:#1F1F1F;">{t}</span>'
            f'<div style="width:120px;height:5px;background:#F2F2F0;border-radius:4px;overflow:hidden;">'
            f'<div style="width:{pct}%;height:100%;background:{color};opacity:0.7;border-radius:4px;"></div>'
            f'</div>'
            f'<span style="font-family:monospace;font-size:0.8rem;color:#6E6E6E;'
            f'min-width:28px;text-align:right;">{cnt}</span>'
            f'</div>'
        )

    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid #E8E8E4;border-radius:16px;'
        f'padding:6px 20px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">{rows_html}</div>',
        unsafe_allow_html=True,
    )
