import re
import os
import tempfile

import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

from analytics.contamination_detector import get_affected_source_nodes
from graph.traversal import get_blast_radius

_ST_INJECT = re.compile(
    r"<script[^>]*>[^<]*Streamlit\.setFrameHeight[^<]*</script>",
    re.IGNORECASE | re.DOTALL,
)

LEVEL_MAP  = {"Supplier": 0, "Distribution Center": 1, "Kitchen": 2, "Store": 3, "Product": 4}
COLOR_MAP  = {"Supplier": "#654A93", "Distribution Center": "#8B6FD8",
              "Kitchen": "#7D6DB7", "Store": "#7FD1C3", "Product": "#E8B7B0"}
BG_MAP     = {"Supplier": "#F5F0FF", "Distribution Center": "#F0EBFE",
              "Kitchen": "#EEE9FB",  "Store": "#E8F8F6",  "Product": "#FDF1F0"}
CRIT_COLOR = "#F15A29"
CRIT_BG    = "#FEF0EB"


def render():
    G = st.session_state.G

    st.markdown("## Graph View")
    st.caption("Supply chain topology and contamination propagation paths.")
    st.markdown("---")

    ctrl, graph_col = st.columns([1, 5])

    with ctrl:
        st.markdown("**Controls**")
        show_c = st.checkbox("Highlight contamination", value=True)
        phys   = st.checkbox("Enable physics",          value=False)

        st.markdown("---")
        st.markdown("**Legend**")
        legend = [
            ("#654A93", "Supplier"),
            ("#8B6FD8", "Dist. Center"),
            ("#7D6DB7", "Kitchen"),
            ("#7FD1C3", "Store"),
            ("#E8B7B0", "Product"),
            ("#F15A29", "Contaminated"),
        ]
        for color, label in legend:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;padding:3px 0;">'
                f'<div style="width:11px;height:11px;border-radius:50%;'
                f'background:{color};flex-shrink:0;"></div>'
                f'<span style="font-size:0.84rem;color:#1F1F1F;">{label}</span></div>',
                unsafe_allow_html=True,
            )

    with graph_col:
        affected: set = set()
        if show_c:
            for src in get_affected_source_nodes(G):
                affected.update(get_blast_radius(G, src).nodes())

        net = Network(
            height="720px",
            width="100%",
            directed=True,
            bgcolor="#FAFAF9",
            font_color="#6E6E6E",
        )

        phys_str = "true" if phys else "false"

        # fit:true makes the graph auto-fit to the container on load — no manual zoom needed
        net.set_options(f"""
        var options = {{
          "layout": {{
            "hierarchical": {{
              "enabled": true,
              "levelSeparation": 180,
              "nodeSpacing": 55,
              "treeSpacing": 80,
              "direction": "LR",
              "sortMethod": "directed"
            }}
          }},
          "nodes": {{
            "borderWidth": 2,
            "borderWidthSelected": 3,
            "shape": "dot",
            "size": 14,
            "font": {{
              "size": 11,
              "face": "Inter, system-ui, sans-serif",
              "color": "#6E6E6E",
              "strokeWidth": 0
            }},
            "shadow": false
          }},
          "edges": {{
            "color": {{
              "inherit": false,
              "color": "rgba(120,120,120,0.18)",
              "highlight": "rgba(139,111,216,0.5)"
            }},
            "smooth": {{
              "type": "cubicBezier",
              "forceDirection": "horizontal",
              "roundness": 0.5
            }},
            "width": 1.5,
            "arrows": {{ "to": {{ "enabled": true, "scaleFactor": 0.5 }} }}
          }},
          "physics": {{ "enabled": {phys_str} }},
          "interaction": {{
            "dragNodes": {phys_str},
            "dragView": true,
            "zoomView": true,
            "hover": true,
            "tooltipDelay": 120,
            "navigationButtons": false
          }}
        }}
        """)

        for node, data in G.nodes(data=True):
            ntype = data.get("type", "Unknown")
            aff   = node in affected
            col   = {"border": CRIT_COLOR if aff else COLOR_MAP.get(ntype, "#9CA3AF"),
                     "background": CRIT_BG if aff else BG_MAP.get(ntype, "#F7F7F5"),
                     "highlight": {"border": CRIT_COLOR if aff else COLOR_MAP.get(ntype, "#9CA3AF"),
                                   "background": "#FDD5C5" if aff else "#EEE9FB"}}
            tip = (f"<b>{data.get('label', node)}</b><br>"
                   f"ID: {node} | Type: {ntype}<br>"
                   f"Location: {data.get('location', data.get('category', 'N/A'))}")
            if aff:
                tip += "<br><b style='color:#F15A29'>⚠ Contaminated</b>"

            net.add_node(node, label=node, title=tip,
                         level=LEVEL_MAP.get(ntype, 0), color=col,
                         borderWidth=3 if aff else 2, size=18 if aff else 13)

        for u, v, edata in G.edges(data=True):
            ae = u in affected and v in affected
            net.add_edge(u, v,
                         title=f"Batch: {edata.get('batch_id','')}",
                         color=CRIT_COLOR if ae else "rgba(120,120,120,0.18)",
                         width=2.5 if ae else 1.5,
                         dashes=[6, 4] if ae else False)

        # Save and strip pyvis Streamlit injection
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as tmp:
            tmp_path = tmp.name
        net.save_graph(tmp_path)
        with open(tmp_path, "r", encoding="utf-8") as f:
            html = f.read()
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

        html = _ST_INJECT.sub("", html)

        # Inject a one-time fit() call so graph fills the container without manual zoom
        fit_script = """
        <script>
        (function waitForNetwork() {
            if (typeof network !== 'undefined') {
                network.fit({ animation: { duration: 600, easingFunction: 'easeInOutQuad' } });
            } else {
                setTimeout(waitForNetwork, 150);
            }
        })();
        </script>"""
        html = html.replace("</body>", fit_script + "</body>")

        st.markdown(
            '<div style="background:#FAFAF9;border:1px solid #E8E8E4;border-radius:16px;'
            'overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.06);">',
            unsafe_allow_html=True,
        )
        components.html(html, height=730, scrolling=False)
        st.markdown("</div>", unsafe_allow_html=True)
