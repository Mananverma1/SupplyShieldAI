import streamlit as st
import pandas as pd
import os, tempfile
from analytics.contamination_detector import get_contaminated_batches, get_affected_source_nodes
from graph.traversal import get_blast_radius
from reports.pdf_report import generate_audit_report

_A = "#8B6FD8"; _D = "#654A93"; _S = "#7FD1C3"; _W = "#F4B860"; _C = "#F15A29"; _P = "#E8B7B0"
_NODE_COLORS = {"Supplier": _D, "Distribution Center": _A, "Kitchen": "#7D6DB7", "Store": _S, "Product": _P}


def _sec(title):
    st.markdown(
        f'<p style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.8px;color:#A0A0A0;padding-bottom:8px;'
        f'border-bottom:1px solid #E8E8E4;margin:2rem 0 1rem 0;">{title}</p>',
        unsafe_allow_html=True,
    )


def render():
    G = st.session_state.G

    st.markdown("## Metrics & Reports")
    st.caption("Lab results, cold chain summary, risk distribution, and exports.")
    st.markdown("---")

    # 1. NODE COMPOSITION
    _sec("Network Node Composition")
    type_counts: dict = {}
    for _, d in G.nodes(data=True):
        t = d.get("type", "Unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
    total_nodes = sum(type_counts.values()) or 1

    rows = ""
    for t, cnt in sorted(type_counts.items(), key=lambda x: -x[1]):
        color = _NODE_COLORS.get(t, "#A0A0A0")
        pct   = round(cnt / total_nodes * 100)
        rows += (
            f'<div style="display:grid;grid-template-columns:14px 1fr 80px 40px;'
            f'gap:14px;align-items:center;padding:10px 20px;border-bottom:1px solid #F7F7F5;">'
            f'<div style="width:10px;height:10px;border-radius:50%;background:{color};"></div>'
            f'<span style="font-size:0.875rem;font-weight:500;color:#1F1F1F;">{t}</span>'
            f'<div style="height:5px;background:#F2F2F0;border-radius:4px;overflow:hidden;">'
            f'<div style="width:{pct}%;height:100%;background:{color};opacity:0.7;border-radius:4px;"></div></div>'
            f'<span style="font-family:monospace;font-size:0.8rem;color:#6E6E6E;text-align:right;">{cnt}</span>'
            f'</div>'
        )
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid #E8E8E4;border-radius:14px;overflow:hidden;">{rows}</div>',
        unsafe_allow_html=True,
    )

    # 2. RISK DISTRIBUTION
    _sec("Risk Score Distribution")
    try:
        from analytics.risk_scoring import score_all_nodes, get_network_risk_summary
        scores  = score_all_nodes(G)
        summary = get_network_risk_summary(scores)
        risk_levels = [("Critical", _C, summary.get("Critical", 0)),
                       ("High Risk", _W, summary.get("High Risk", 0)),
                       ("Investigate", _A, summary.get("Investigate", 0)),
                       ("Safe", _S, summary.get("Safe", 0))]
        total_s = sum(v for _, _, v in risk_levels) or 1
        bars = ""
        for lbl, color, count in risk_levels:
            pct = round(count / total_s * 100)
            bars += (
                f'<div style="display:grid;grid-template-columns:110px 1fr 36px;'
                f'gap:12px;align-items:center;margin-bottom:10px;">'
                f'<span style="font-size:0.8rem;font-weight:600;color:#1F1F1F;">{lbl}</span>'
                f'<div style="height:8px;background:#F2F2F0;border-radius:6px;overflow:hidden;">'
                f'<div style="width:{pct}%;height:100%;background:{color};border-radius:6px;"></div></div>'
                f'<span style="font-family:monospace;font-size:0.78rem;color:#6E6E6E;">{count}</span>'
                f'</div>'
            )
        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #E8E8E4;border-radius:14px;padding:20px 22px;">{bars}</div>',
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.warning(f"Risk scoring unavailable: {e}")

    # 3. LAB RESULTS
    _sec("Recent Lab Results")
    contaminated_batches = get_contaminated_batches()
    try:
        lab_df = pd.read_csv("data/lab_results.csv")
        pass_c = int((lab_df["result"] == "Pass").sum())
        fail_c = int((lab_df["result"] == "Fail").sum())
        total_t = len(lab_df)
        rate   = round(pass_c / total_t * 100, 1) if total_t else 0.0
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Total Tests", total_t)
        with m2: st.metric("Passed", pass_c)
        with m3: st.metric("Failed", fail_c)
        with m4: st.metric("Pass Rate", f"{rate}%")
        st.markdown("<br>", unsafe_allow_html=True)
        lab_view = lab_df.sort_values("test_date", ascending=False).head(20)
        def _ls(row):
            if str(row.get("result","")).lower() == "fail":
                return ["background:#FEF0EB;color:#5A1A06"] * len(row)
            return ["background:#EBF9F7;color:#1A5F55"] * len(row)
        st.dataframe(lab_view.style.apply(_ls, axis=1), use_container_width=True,
                     height=min(360, 56 + len(lab_view) * 36), hide_index=True)
    except Exception:
        st.error("Could not load lab results.")

    # 4. COLD CHAIN SUMMARY
    _sec("Cold Chain — Temperature Summary")
    try:
        tlog = pd.read_csv("data/transport_logs.csv")
        br   = tlog[tlog["temperature"] > 45.0]
        el   = tlog[(tlog["temperature"] > 41.0) & (tlog["temperature"] <= 45.0)]
        t1, t2, t3, t4 = st.columns(4)
        with t1: st.metric("Legs Monitored", len(tlog))
        with t2: st.metric("Breaches >45°F", len(br))
        with t3: st.metric("Elevated 41-45°F", len(el))
        with t4: st.metric("Avg Temp", f"{round(tlog['temperature'].mean(),1)}°F")
        if not br.empty:
            st.markdown("<br>", unsafe_allow_html=True)
            off = pd.concat([
                br[["from_id","temperature"]].rename(columns={"from_id":"node"}),
                br[["to_id","temperature"]].rename(columns={"to_id":"node"}),
            ]).groupby("node").agg(breaches=("temperature","count"), max_temp=("temperature","max"))
            off = off.sort_values("breaches", ascending=False).head(8).reset_index()
            off.columns = ["Node ID","Breach Count","Max Temp (°F)"]
            st.dataframe(off, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Could not load transport logs: {e}")

    # 5. CUSTOMER COMPLAINTS
    _sec("Customer Complaints")
    try:
        comp = pd.read_csv("data/customer_complaints.csv").sort_values("date", ascending=False).head(20)
        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Total", len(comp))
        def _sev(s):
            try: return int((comp["severity"] == s).sum())
            except: return 0
        with c2: st.metric("High", _sev("High"))
        with c3: st.metric("Medium", _sev("Medium"))
        with c4: st.metric("Low", _sev("Low"))
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(comp, use_container_width=True, hide_index=True, height=min(360, 56 + len(comp) * 36))
    except Exception:
        st.error("Could not load complaints.")

    # 6. EXPORT
    _sec("Export Reports")
    a_sources = get_affected_source_nodes(G)
    a_nodes: set = set()
    for s in a_sources:
        a_nodes.update(get_blast_radius(G, s).nodes())

    pdf_bytes = None
    tmp = os.path.join(tempfile.gettempdir(), f"SS_{os.urandom(4).hex()}.pdf")
    try:
        generate_audit_report(G, contaminated_batches, a_nodes, tmp)
        with open(tmp, "rb") as f:
            pdf_bytes = f.read()
    except Exception as ex:
        st.warning(f"PDF generation failed: {ex}")
    finally:
        try:
            if os.path.exists(tmp): os.remove(tmp)
        except Exception: pass

    csv_rows = [{"node_id": n, "type": G.nodes[n].get("type",""),
                 "name": G.nodes[n].get("label", n),
                 "location": G.nodes[n].get("location", G.nodes[n].get("category",""))}
                for n in sorted(a_nodes)]
    csv_data = pd.DataFrame(csv_rows).to_csv(index=False) if csv_rows else "no affected nodes"

    p1, p2, _ = st.columns([2, 2, 6])
    with p1:
        if pdf_bytes:
            st.download_button("📄  Download PDF", data=pdf_bytes,
                               file_name="SupplyShield_Audit_Report.pdf",
                               mime="application/pdf", use_container_width=True)
        else:
            st.button("📄  Download PDF", disabled=True, use_container_width=True)
    with p2:
        st.download_button("📊  Download CSV", data=csv_data,
                           file_name="SupplyShield_Affected_Nodes.csv",
                           mime="text/csv", use_container_width=True)
