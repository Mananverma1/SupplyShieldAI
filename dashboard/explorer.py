import streamlit as st

_TYPE_CONFIG = {
    "Supplier":            ("#EEE9FB", "#654A93", "#654A93"),
    "Distribution Center": ("#F0EBFE", "#8B6FD8", "#8B6FD8"),
    "Kitchen":             ("#EEE9FB", "#7D6DB7", "#7D6DB7"),
    "Store":               ("#E8F8F6", "#1A8878", "#7FD1C3"),
    "Product":             ("#FDF1F0", "#9A4A40", "#E8B7B0"),
}


def render():
    G = st.session_state.G

    st.markdown("## Chain Explorer")
    st.caption("Inspect any node in the supply chain network.")
    st.markdown("---")

    raw = st.text_input(
        "Search node",
        placeholder="Enter a node ID — e.g. SUP-001, DC-003, KIT-002, PRD-008, ST-005",
        label_visibility="collapsed",
    )

    if not raw:
        all_ids = sorted(G.nodes())
        sample  = all_ids[:18]
        chips   = "  ".join(
            f'<code style="background:#F0EBFE;color:#654A93;padding:2px 7px;'
            f'border-radius:6px;font-size:0.78rem;">{n}</code>' for n in sample
        )
        extra = (
            f'  <span style="color:#A0A0A0;font-size:0.8rem;">and {len(all_ids)-18} more…</span>'
            if len(all_ids) > 18 else ""
        )
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E8E8E4;border-radius:14px;'
            f'padding:18px 22px;font-size:0.875rem;color:#6E6E6E;line-height:2.2;">'
            f'💡 Enter a node ID above to explore it.<br>{chips}{extra}</div>',
            unsafe_allow_html=True,
        )
        return

    node_id = raw.strip().upper()

    if node_id not in G.nodes():
        close = [n for n in G.nodes() if node_id in n or n.startswith(node_id[:3])]
        sug = ""
        if close:
            sug = "  Did you mean: " + "  ".join(
                f'<code style="background:#F0EBFE;color:#654A93;padding:1px 6px;border-radius:4px;">{n}</code>'
                for n in close[:6]
            )
        st.markdown(
            f'<div style="text-align:center;padding:60px 20px;">'
            f'<div style="font-size:2.5rem;margin-bottom:12px;">🔍</div>'
            f'<p style="font-size:1rem;font-weight:600;color:#1F1F1F;margin:0 0 5px 0;">'
            f'Node not found: <code>{node_id}</code></p>'
            f'<p style="font-size:0.875rem;color:#A0A0A0;margin:0;">Check the ID and try again.{sug}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        return

    # ── Node found ──────────────────────────────────────────────────
    data  = G.nodes[node_id]
    ntype = data.get("type", "Unknown")
    label = data.get("label", node_id)
    pill_bg, pill_color, dot_color = _TYPE_CONFIG.get(ntype, ("#F2F2F0", "#6E6E6E", "#A0A0A0"))

    successors   = list(G.successors(node_id))
    predecessors = list(G.predecessors(node_id))

    # ── Header card ─────────────────────────────────────────────────
    st.markdown(
        f'<div style="background:{pill_bg}33;border:1px solid {pill_bg};border-radius:16px;'
        f'padding:18px 24px;display:flex;align-items:center;justify-content:space-between;'
        f'margin-bottom:16px;">'
        f'<div>'
        f'<div style="font-size:1.1rem;font-weight:700;color:#1F1F1F;">{label}</div>'
        f'<div style="font-family:monospace;font-size:0.78rem;color:#A0A0A0;margin-top:2px;">{node_id}</div>'
        f'</div>'
        f'<span style="background:{pill_bg};color:{pill_color};padding:5px 14px;'
        f'border-radius:999px;font-size:0.72rem;font-weight:700;">{ntype}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Two columns: Properties | Connections ───────────────────────
    col_prop, col_conn = st.columns(2)

    with col_prop:
        st.markdown(
            '<p style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            'letter-spacing:0.8px;color:#A0A0A0;margin-bottom:10px;">Properties</p>',
            unsafe_allow_html=True,
        )
        skip = {"type", "label"}
        has_props = False
        for k, v in data.items():
            if k in skip:
                continue
            has_props = True
            st.markdown(
                f'<div style="display:flex;gap:10px;padding:7px 0;'
                f'border-bottom:1px solid #F7F7F5;font-size:0.875rem;">'
                f'<span style="color:#A0A0A0;font-weight:500;min-width:90px;flex-shrink:0;">'
                f'{k.capitalize()}</span>'
                f'<span style="color:#1F1F1F;font-weight:500;">{v}</span></div>',
                unsafe_allow_html=True,
            )
        if not has_props:
            st.caption("No additional properties.")

    with col_conn:
        st.markdown(
            '<p style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
            'letter-spacing:0.8px;color:#A0A0A0;margin-bottom:10px;">Connections</p>',
            unsafe_allow_html=True,
        )

        def _conn_section(title, nodes):
            count_pill = (
                f'<span style="background:#F2F0F9;color:#8B6FD8;font-size:0.65rem;'
                f'font-weight:700;padding:1px 8px;border-radius:999px;">{len(nodes)}</span>'
            )
            st.markdown(
                f'<p style="font-size:0.75rem;font-weight:600;color:#6E6E6E;'
                f'margin:0 0 8px 0;">{title} {count_pill}</p>',
                unsafe_allow_html=True,
            )
            if not nodes:
                st.caption("None")
                return
            for n in nodes[:20]:
                nt = G.nodes[n].get("type", "")
                _, _, dc = _TYPE_CONFIG.get(nt, ("", "", "#A0A0A0"))
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:9px;padding:7px 0;'
                    f'border-bottom:1px solid #F7F7F5;">'
                    f'<div style="width:8px;height:8px;border-radius:50%;'
                    f'background:{dc};flex-shrink:0;"></div>'
                    f'<div><div style="font-family:monospace;font-size:0.78rem;'
                    f'font-weight:600;color:#8B6FD8;">{n}</div>'
                    f'<div style="font-size:0.72rem;color:#A0A0A0;">{nt}</div></div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            if len(nodes) > 20:
                st.caption(f"…and {len(nodes)-20} more")

        _conn_section("Supplies to", successors)
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        _conn_section("Receives from", predecessors)
