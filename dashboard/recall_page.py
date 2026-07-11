import streamlit as st
import pandas as pd
from analytics.contamination_detector import get_affected_source_nodes
from graph.traversal import get_blast_radius

_C = "#F15A29"; _W = "#F4B860"; _S = "#7FD1C3"; _A = "#8B6FD8"


def _build_df(G, affected_nodes):
    rows = []
    for node in sorted(affected_nodes):
        d = G.nodes[node]
        ntype = d.get("type", "Unknown")
        rows.append({
            "Node ID": node, "Type": ntype,
            "Name": d.get("label", node),
            "Location": d.get("location", d.get("category", "—")),
            "Required Action": "Stop Sale / Destroy" if ntype == "Product" else "Sanitize / Quarantine",
            "Priority": "High" if ntype in ("Product", "Store") else "Medium",
        })
    return pd.DataFrame(rows)


def render():
    if "recall_issued" not in st.session_state:
        st.session_state.recall_issued = False
    if "recall_confirmed" not in st.session_state:
        st.session_state.recall_confirmed = False

    G = st.session_state.G

    st.markdown("## Recall Center")
    st.caption("Actionable intelligence for product recalls and facility containment.")
    st.markdown("---")

    affected_sources = get_affected_source_nodes(G)

    if not affected_sources:
        st.success("✅ **All Clear — No Active Recalls.** All supply chain nodes are operating within safe parameters.")
        return

    affected_nodes: set = set()
    for src in affected_sources:
        affected_nodes.update(get_blast_radius(G, src).nodes())

    df = _build_df(G, affected_nodes)
    high_count   = int((df["Priority"] == "High").sum())
    medium_count = int((df["Priority"] == "Medium").sum())

    # Alert banner
    st.error(f"⚠️ **Active Contamination Event** — {len(affected_sources)} source trigger(s). "
             f"{len(affected_nodes)} downstream nodes require immediate action.")

    # Stat row
    s1, s2, s3, s4 = st.columns(4)
    with s1: st.metric("Source Triggers", len(affected_sources))
    with s2: st.metric("Nodes at Risk",   len(affected_nodes))
    with s3: st.metric("High Priority",   high_count)
    with s4: st.metric("Medium Priority", medium_count)

    st.markdown("---")
    st.markdown("**Blast Radius — Action Plan**")

    def _row_style(row):
        if row["Priority"] == "High":
            return ["background:#FEF0EB;color:#5A1A06"] * len(row)
        return ["background:#FEF6E8;color:#5A3A06"] * len(row)

    st.dataframe(
        df.style.apply(_row_style, axis=1),
        use_container_width=True,
        height=min(440, 56 + len(df) * 36),
    )

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, _ = st.columns([2, 2, 6])
    with c1:
        if not st.session_state.recall_issued and not st.session_state.recall_confirmed:
            if st.button("🔔  Issue Recall Notices", type="primary", use_container_width=True):
                st.session_state.recall_issued = True
                st.rerun()
    with c2:
        st.download_button(
            "⬇  Export CSV", data=df.to_csv(index=False),
            file_name="recall_report.csv", mime="text/csv", use_container_width=True,
        )

    if st.session_state.recall_issued and not st.session_state.recall_confirmed:
        st.warning(
            f"⚠️ **Confirm Recall Broadcast** — This will dispatch notices to all "
            f"**{len(affected_nodes)} affected nodes** ({high_count} high-priority, "
            f"{medium_count} medium-priority). This action cannot be undone."
        )
        ca, cb, _ = st.columns([2, 1.6, 6.4])
        with ca:
            if st.button("✓  Confirm & Send", type="primary", use_container_width=True, key="rc_confirm"):
                st.session_state.recall_confirmed = True
                st.session_state.recall_issued    = False
                st.rerun()
        with cb:
            if st.button("✕  Cancel", use_container_width=True, key="rc_cancel"):
                st.session_state.recall_issued = False
                st.rerun()

    if st.session_state.recall_confirmed:
        preview = ", ".join(sorted(affected_nodes)[:6])
        if len(affected_nodes) > 6:
            preview += f" +{len(affected_nodes)-6} more"
        st.success(f"✅ **Recall Notices Dispatched** — {len(affected_nodes)} nodes notified. "
                   f"**Nodes:** {preview}")
        col_r, _ = st.columns([2, 8])
        with col_r:
            if st.button("↺  New Recall", use_container_width=True, key="rc_reset"):
                st.session_state.recall_confirmed = False
                st.session_state.recall_issued    = False
                st.rerun()
