import streamlit as st
import pandas as pd
import numpy as np

_A = "#8B6FD8"; _S = "#7FD1C3"; _W = "#F4B860"; _C = "#F15A29"
SAFE_MAX = 41.0
WARN_MAX = 45.0


def _temp_pill(t):
    if t > WARN_MAX:
        return f'<span style="background:#FEF0EB;color:{_C};border:1px solid #F9C3B1;padding:3px 10px;border-radius:999px;font-size:0.75rem;font-weight:700;">🌡️ {t}°F</span>'
    if t > SAFE_MAX:
        return f'<span style="background:#FEF6E8;color:{_W};border:1px solid #F4D17A;padding:3px 10px;border-radius:999px;font-size:0.75rem;font-weight:700;">🌡️ {t}°F</span>'
    return f'<span style="background:#EBF9F7;color:{_S};border:1px solid #B2E8E1;padding:3px 10px;border-radius:999px;font-size:0.75rem;font-weight:700;">🌡️ {t}°F</span>'


def _sec(title):
    st.markdown(
        f'<p style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.8px;color:#A0A0A0;padding-bottom:8px;'
        f'border-bottom:1px solid #E8E8E4;margin:2rem 0 1rem 0;">{title}</p>',
        unsafe_allow_html=True,
    )


def render():
    st.markdown("## Cold Chain Monitoring")
    st.caption("IoT temperature tracking across transport legs — spoilage risk detection.")
    st.markdown("---")

    try:
        df = pd.read_csv("data/transport_logs.csv")
    except Exception:
        st.error("Could not load transport_logs.csv")
        return

    breaches = df[df["temperature"] > WARN_MAX]
    elevated = df[(df["temperature"] > SAFE_MAX) & (df["temperature"] <= WARN_MAX)]
    avg_temp = round(df["temperature"].mean(), 1)

    # Stat row
    s1, s2, s3, s4 = st.columns(4)
    with s1: st.metric("Legs Monitored",    len(df))
    with s2: st.metric("Breaches >45°F",    len(breaches))
    with s3: st.metric("Elevated 41-45°F",  len(elevated))
    with s4: st.metric("Avg Temperature",   f"{avg_temp}°F")

    # Legend
    st.markdown(
        f'<div style="display:flex;gap:20px;margin:12px 0;flex-wrap:wrap;">'
        f'<span style="font-size:0.82rem;color:#6E6E6E;display:flex;align-items:center;gap:7px;">'
        f'<span style="width:10px;height:10px;border-radius:50%;background:{_S};display:inline-block;"></span>Safe ≤41°F</span>'
        f'<span style="font-size:0.82rem;color:#6E6E6E;display:flex;align-items:center;gap:7px;">'
        f'<span style="width:10px;height:10px;border-radius:50%;background:{_W};display:inline-block;"></span>Elevated 41-45°F</span>'
        f'<span style="font-size:0.82rem;color:#6E6E6E;display:flex;align-items:center;gap:7px;">'
        f'<span style="width:10px;height:10px;border-radius:50%;background:{_C};display:inline-block;"></span>Breach >45°F</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Distribution chart (native Streamlit — no iframe issues)
    _sec("Temperature Distribution Across All Legs")
    bins = list(range(20, 58, 2))
    hist, edges = np.histogram(df["temperature"].dropna(), bins=bins)
    hist_df = pd.DataFrame({
        "Range (°F)": [f"{int(edges[i])}-{int(edges[i+1])}" for i in range(len(hist))],
        "Count": hist,
    }).set_index("Range (°F)")
    st.bar_chart(hist_df, height=200, use_container_width=True)

    # Per-node breach exposure
    _sec("Nodes with Highest Breach Exposure")
    if not breaches.empty:
        off = pd.concat([
            breaches[["from_id","temperature"]].rename(columns={"from_id":"node"}),
            breaches[["to_id","temperature"]].rename(columns={"to_id":"node"}),
        ]).groupby("node").agg(
            breach_count=("temperature","count"), max_temp=("temperature","max")
        ).sort_values("breach_count", ascending=False).head(10).reset_index()
        off.columns = ["Node ID","Breach Count","Max Temp (°F)"]
        st.dataframe(off, use_container_width=True, hide_index=True)
    else:
        st.info("No breaches detected.")

    # Breach log
    _sec("Temperature Breach Log (>45°F)")
    if breaches.empty:
        st.success("No temperature breaches. Cold chain is intact.")
        return

    rows_html = ""
    for _, row in breaches.sort_values("temperature", ascending=False).iterrows():
        rows_html += (
            f'<div style="display:grid;grid-template-columns:2fr 2fr 1.5fr 1.5fr 1fr;'
            f'gap:8px;align-items:center;padding:10px 20px;border-bottom:1px solid #F7F7F5;font-size:0.84rem;">'
            f'<span style="font-family:monospace;font-size:0.75rem;font-weight:600;color:#654A93;">{row["log_id"]}</span>'
            f'<span style="font-family:monospace;font-size:0.75rem;font-weight:600;color:#654A93;">{row["batch_id"]}</span>'
            f'<span style="color:#1F1F1F;font-weight:500;">{row["from_id"]}</span>'
            f'<span style="color:#1F1F1F;font-weight:500;">{row["to_id"]}</span>'
            f'{_temp_pill(row["temperature"])}'
            f'</div>'
        )
    header = (
        '<div style="display:grid;grid-template-columns:2fr 2fr 1.5fr 1.5fr 1fr;'
        'gap:8px;padding:10px 20px;background:#F7F7F5;border-bottom:1px solid #E8E8E4;'
        'font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;color:#A0A0A0;">'
        '<div>Log ID</div><div>Batch ID</div><div>From</div><div>To</div><div>Temp</div></div>'
    )
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid #E8E8E4;border-radius:14px;overflow:hidden;">'
        f'{header}{rows_html}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, _ = st.columns([2, 8])
    with col1:
        st.download_button("⬇  Export Breach Log", data=breaches.to_csv(index=False),
                           file_name="temperature_breaches.csv", mime="text/csv",
                           use_container_width=True)
