import streamlit as st
import pandas as pd
import networkx as nx
from analytics.risk_scoring import score_all_nodes, get_network_risk_summary, get_recall_efficiency
from analytics.contamination_detector import get_affected_source_nodes
from graph.traversal import get_root_causes, get_blast_radius

_A = "#8B6FD8"; _D = "#654A93"; _S = "#7FD1C3"; _W = "#F4B860"; _C = "#F15A29"
_LEVEL_BG = {"Critical": ("#FEF0EB", _C, "#F9C3B1"),
             "High Risk": ("#FEF6E8", _W, "#F4D17A"),
             "Investigate": ("#F0EBFE", _A, "#C4B3F0"),
             "Safe": ("#EBF9F7", _S, "#B2E8E1")}
_TYPE_COLORS = {"Supplier": _D, "Distribution Center": _A,
                "Kitchen": "#7D6DB7", "Store": _S, "Product": "#E8B7B0"}


def _sec(title):
    st.markdown(
        f'<p style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.8px;color:#A0A0A0;padding-bottom:8px;'
        f'border-bottom:1px solid #E8E8E4;margin:2rem 0 1rem 0;">{title}</p>',
        unsafe_allow_html=True,
    )


def render():
    if "recall_issued" not in st.session_state:
        st.session_state.recall_issued = False
    if "recall_confirmed" not in st.session_state:
        st.session_state.recall_confirmed = False

    G = st.session_state.G

    st.markdown("## Risk Analysis")
    st.caption("Risk scoring, root cause tracing, and recall efficiency across the supply chain.")
    st.markdown("---")

    with st.spinner("Calculating risk scores…"):
        scores  = score_all_nodes(G)
    summary = get_network_risk_summary(scores)

    a_sources = get_affected_source_nodes(G)
    a_nodes: set = set()
    for src in a_sources:
        a_nodes.update(get_blast_radius(G, src).nodes())
    eff = get_recall_efficiency(G, a_nodes)

    # Level summary cards
    levels = [("Critical", summary["Critical"], _C, "#FEF0EB", "#F9C3B1"),
              ("High Risk", summary["High Risk"], _W, "#FEF6E8", "#F4D17A"),
              ("Investigate", summary["Investigate"], _A, "#F0EBFE", "#C4B3F0"),
              ("Safe", summary["Safe"], _S, "#EBF9F7", "#B2E8E1")]

    l1, l2, l3, l4 = st.columns(4)
    for col, (lbl, count, color, bg, border) in zip([l1,l2,l3,l4], levels):
        with col:
            st.markdown(
                f'<div style="background:{bg};border:1.5px solid {border};border-radius:16px;'
                f'padding:18px 22px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">'
                f'<p style="font-family:monospace;font-size:2.2rem;font-weight:600;'
                f'color:{color};letter-spacing:-1px;margin:0 0 4px 0;">{count}</p>'
                f'<p style="font-size:0.68rem;font-weight:700;text-transform:uppercase;'
                f'letter-spacing:0.8px;color:{color};margin:0;">{lbl}</p></div>',
                unsafe_allow_html=True,
            )

    # Recall efficiency
    _sec("Recall Efficiency — Targeted vs. National")
    e1, e2, e3, e4 = st.columns(4)
    with e1: st.metric("Total Network",    eff["total_nodes"])
    with e2: st.metric("Targeted Recall",  eff["targeted"])
    with e3: st.metric("Nodes Saved",      eff["saved"])
    with e4: st.metric("Efficiency",       f"{eff['efficiency_pct']}%")

    # Top risk nodes table
    _sec("Top Risk Nodes (ranked by score)")
    top = sorted(scores.items(), key=lambda x: -x[1]["score"])[:30]
    table_rows = []
    for nid, s in top:
        bg, color, _ = _LEVEL_BG.get(s["level"], ("#F7F7F5", "#6E6E6E", "#E8E8E4"))
        # Professional, compact symbols for easier scanning in the Signals column
        signals = ("🧬" if s["lab_fail"] else "")
        # Breach / contamination detected
        signals += (" ⛔" if s["breach"] else "")
        # Complaints is numeric/count; show the count next to an envelope icon
        signals += (f" ✉{s['complaints']}" if s["complaints"] else "")
        table_rows.append({
            "Node ID": nid, "Type": s["type"], "Score": s["score"],
            "Level": s["level"], "Signals": signals.strip(), "Spread": s["spread"],
        })
    if table_rows:
        df_risk = pd.DataFrame(table_rows)
        def _rs(row):
            bg, color, _ = _LEVEL_BG.get(row["Level"], ("#F7F7F5","#6E6E6E","#E8E8E4"))
            return [f"background:{bg};color:{color}" if col == "Level" else "" for col in row.index]
        st.dataframe(df_risk.style.apply(_rs, axis=1), use_container_width=True,
                     height=min(600, 56 + len(df_risk) * 36), hide_index=True)

    # Root Cause Analysis
    _sec("Root Cause Analysis — Upstream Trace")
    st.caption("Select a node to trace its upstream contamination path back to the root source.")
    target = st.selectbox("Trace from node:", options=sorted(G.nodes()),
                          label_visibility="collapsed", key="rca_target")

    if target:
        rca = get_root_causes(G, target)
        if rca.number_of_nodes() <= 1:
            st.info("No upstream ancestors found for this node.")
        else:
            try:
                order = list(nx.topological_sort(rca))
            except Exception:
                order = list(rca.nodes())

            path_parts = []
            for i, nid in enumerate(order):
                ntype = G.nodes[nid].get("type", "")
                nc    = _TYPE_COLORS.get(ntype, "#A0A0A0")
                border = f"border:2px solid {_C}" if nid == target else "border:1px solid #E8E8E4"
                path_parts.append(
                    f'<div style="display:inline-flex;flex-direction:column;align-items:center;'
                    f'background:#F7F7F5;{border};border-radius:10px;padding:7px 13px;'
                    f'min-width:75px;text-align:center;">'
                    f'<span style="font-family:monospace;font-size:0.72rem;font-weight:700;'
                    f'color:{nc};">{nid}</span>'
                    f'<span style="font-size:0.6rem;color:#A0A0A0;margin-top:2px;">{ntype}</span>'
                    f'</div>'
                )
                if i < len(order) - 1:
                    path_parts.append('<span style="color:#A0A0A0;font-size:1rem;align-self:center;">→</span>')

            st.markdown(
                f'<div style="display:flex;flex-wrap:wrap;align-items:center;gap:6px;'
                f'background:#FFFFFF;border:1px solid #E8E8E4;border-radius:14px;padding:16px 20px;">'
                f'{"".join(path_parts)}</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"{rca.number_of_nodes()} upstream nodes traced. "
                       f"Target node {target} shown with orange border.")
