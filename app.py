"""
ARM Market Intelligence Platform — Public Demo
Author  : Vibhash | Senior Market Intelligence Analyst, Arm Ltd
Zero external dependencies — only Streamlit (built-in charts).
No pandas, numpy, or plotly needed — deploys on any Python version.
"""

import streamlit as st
import random
from datetime import date

st.set_page_config(
    page_title="ARM Market Intelligence",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

ARM_BLUE = "#0070C0"
st.markdown(f"""
<style>
  [data-testid="stMetricValue"] {{ font-size:2rem; font-weight:700; color:{ARM_BLUE}; }}
  [data-testid="stMetricDelta"] {{ font-size:0.9rem; }}
  .stTabs [data-baseweb="tab"]  {{ font-weight:600; font-size:0.95rem; }}
  .block-container              {{ padding-top:1rem; }}
</style>
""", unsafe_allow_html=True)

# ── Synthetic Data (pure Python — no numpy/pandas) ───────────────────────────
random.seed(42)
LOBS     = ["Mobile", "IoT", "Automotive", "Infrastructure"]
QUARTERS = [f"Q{q}'{str(y)[2:]}" for y in range(2022,2025) for q in range(1,5)]
BASE     = {"Mobile":412,"IoT":98,"Automotive":41,"Infrastructure":187}
GROWTH   = {"Mobile":0.028,"IoT":0.033,"Automotive":0.072,"Infrastructure":0.035}

revenue = {}
for lob in LOBS:
    rev, s = BASE[lob], []
    for _ in QUARTERS:
        rev = rev*(1+GROWTH[lob]) + random.gauss(0, rev*0.01)
        s.append(round(rev,1))
    revenue[lob] = s

v9 = [round(18+i*1.7+random.gauss(0,0.3),1) for i in range(12)]
v8 = [round(52-i*0.7+random.gauss(0,0.3),1) for i in range(12)]
v7 = [round(max(0,100-v9[i]-v8[i]),1)        for i in range(12)]

pipeline = {
    "Won":      {"Mobile":2400,"IoT":820, "Automotive":610, "Infrastructure":2370},
    "Active":   {"Mobile":3800,"IoT":1240,"Automotive":890, "Infrastructure":3870},
    "Lost":     {"Mobile":920, "IoT":310, "Automotive":270, "Infrastructure":680},
}
tam = {
    "Mobile":         {"tam":280,"addr":68, "actual":2.84},
    "IoT":            {"tam":95, "addr":22, "actual":0.54},
    "Automotive":     {"tam":72, "addr":18, "actual":0.34},
    "Infrastructure": {"tam":174,"addr":40, "actual":0.88},
}
riscv = {
    "Mobile":         {"m":890,"pct":23.4},
    "IoT":            {"m":380,"pct":30.6},
    "Automotive":     {"m":290,"pct":32.6},
    "Infrastructure": {"m":600,"pct":15.5},
}
rv_trend = {
    "Mobile":[14.1,17.8,23.4],"IoT":[18.2,23.1,30.6],
    "Automotive":[19.4,25.3,32.6],"Infrastructure":[9.2,11.8,15.5],
}
licensees = [
    ("Qualcomm","Mobile",591,"2,940M","$0.201","v9","Tier-1"),
    ("Samsung","Mobile",432,"3,210M","$0.135","v9","Tier-1"),
    ("Apple","Mobile",389,"1,820M","$0.214","v9","Tier-1"),
    ("MediaTek","Mobile",218,"4,100M","$0.053","v8","Tier-1"),
    ("NVIDIA","Infrastructure",187,"640M","$0.292","v9","Tier-1"),
    ("Amazon (Graviton)","Infrastructure",141,"480M","$0.294","v9","Tier-2"),
    ("Broadcom","Infrastructure",128,"920M","$0.139","v8","Tier-2"),
    ("NXP","Automotive",92,"1,280M","$0.072","v8","Tier-2"),
    ("Renesas","Automotive",71,"980M","$0.072","v8","Tier-2"),
    ("STMicro","IoT",64,"3,200M","$0.020","v7","Tier-2"),
]
quality_data = [
    {"table":"royalty_revenue_raw","records":1_284_192,"anom":153,"rate":0.012,"pass":True,"run":"04:18","n":12},
    {"table":"design_wins_raw","records":48_311,"anom":0,"rate":0.000,"pass":True,"run":"04:22","n":8},
    {"table":"tam_forecasts_raw","records":12_840,"anom":0,"rate":0.000,"pass":True,"run":"04:24","n":5},
]

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='font-size:1.6rem;font-weight:700;color:{ARM_BLUE}'>🔷 ARM MI</div>",unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.75rem;color:gray;margin-bottom:1rem'>Market Intelligence Platform</div>",unsafe_allow_html=True)
    lob_choice = st.selectbox("Line of Business", ["All"]+LOBS)
    year_range = st.slider("Fiscal Year", 2022, 2024, (2022, 2024))
    scenario   = st.radio("TAM Scenario", ["Base","Bull","Bear"], horizontal=True)
    st.markdown("---")
    if st.button("🔄 Refresh"): st.rerun()
    st.caption(f"Data: {date.today().strftime('%d %b %Y')} · Synthetic demo")

q_idx   = [i for i in range(12) if year_range[0] <= 2022+i//4 <= year_range[1]]
ql      = [QUARTERS[i] for i in q_idx]
lobs_s  = [lob_choice] if lob_choice != "All" else LOBS

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("# 🔷 ARM Market Intelligence Platform")
st.markdown(f"**Royalty · Pipeline · TAM · RISC-V** — LOB: `{lob_choice}` | FY: `{year_range[0]}–{year_range[1]}`")
st.markdown('<div style="background:#1A1A2E;color:#BDD7EE;padding:0.4rem 1rem;border-radius:6px;font-size:0.78rem">📊 Public demo — synthetic data. Production: Databricks Delta Lake + Unity Catalog.</div>',unsafe_allow_html=True)
st.divider()

tab1,tab2,tab3,tab4,tab5 = st.tabs(["📊 Royalty Revenue","🏆 Design Win Pipeline","🌍 TAM & Market Share","🔴 RISC-V Threat","🔧 Data Quality"])

# ── TAB 1 ─────────────────────────────────────────────────────────────────────
with tab1:
    total_rev = sum(revenue[l][i] for l in lobs_s for i in q_idx)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Royalty (period)", f"${total_rev:,.0f}M")
    c2.metric("Latest v9 Share",        f"{v9[-1]:.1f}%", delta="+6.1pp QoQ")
    c3.metric("Active Licensees",       f"{sum(BASE[l]//3+24 for l in lobs_s):,}")
    c4.metric("Avg RPU",                f"${0.046+len(q_idx)*0.001:.4f}", delta="+$0.003")
    st.markdown("---")
    ca,cb = st.columns(2)
    with ca:
        st.markdown("**Quarterly Royalty Revenue by LOB (USD M)**")
        chart = {l:[revenue[l][i] for i in q_idx] for l in lobs_s}
        st.line_chart(chart, height=260)
        st.caption(f"Quarters: {ql[0] if ql else '—'} → {ql[-1] if ql else '—'}")
    with cb:
        st.markdown("**Architecture Mix — v9 / v8 / v7 (%)**")
        st.area_chart({"v9":[v9[i] for i in q_idx],"v8":[v8[i] for i in q_idx],"v7":[v7[i] for i in q_idx]}, height=260)
        st.caption(f"Quarters: {ql[0] if ql else '—'} → {ql[-1] if ql else '—'}")
    st.markdown("#### Licensee Leaderboard — Top 10 (FY 2024)")
    rows = [l for l in licensees if lob_choice=="All" or l[1]==lob_choice]
    if rows:
        st.dataframe({"#":list(range(1,len(rows)+1)),"Licensee":[r[0] for r in rows],"LOB":[r[1] for r in rows],
            "Revenue (USD M)":[r[2] for r in rows],"Units":[r[3] for r in rows],
            "Avg RPU":[r[4] for r in rows],"Arch":[r[5] for r in rows],"Tier":[r[6] for r in rows]},
            use_container_width=True, hide_index=True)
    else:
        st.info("No licensees for selected LOB.")

# ── TAB 2 ─────────────────────────────────────────────────────────────────────
with tab2:
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Won Deals",       "214")
    c2.metric("Won Revenue",     f"${sum(pipeline['Won'].values())/1000:.1f}B")
    c3.metric("Active Pipeline", f"${sum(pipeline['Active'].values())/1000:.1f}B")
    c4.metric("Avg Win Rate",    "61.4%", delta="+3.2pp")
    ca,cb = st.columns(2)
    with ca:
        st.markdown("**Risk-Adjusted Pipeline by LOB & Stage (USD M)**")
        st.bar_chart({s:[pipeline[s][l] for l in lobs_s] for s in ["Won","Active","Lost"]}, height=280)
        st.caption("Groups: "+(" | ".join(lobs_s)))
    with cb:
        st.markdown("**Competitor Split (%)**")
        st.dataframe({"Competitor":["Proprietary","RISC-V","Other","x86","MIPS"],
            "Pipeline %":[31,22,21,18,8],"At Risk USD M":[3100,2160,2050,1800,780]},
            use_container_width=True, hide_index=True)
        st.bar_chart({"Pipeline %":[31,22,21,18,8]}, height=160)
        st.caption("Proprietary | RISC-V | Other | x86 | MIPS")

# ── TAB 3 ─────────────────────────────────────────────────────────────────────
with tab3:
    tt = sum(tam[l]["tam"]    for l in lobs_s)
    ta = sum(tam[l]["addr"]   for l in lobs_s)
    tr = sum(tam[l]["actual"] for l in lobs_s)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total TAM",              f"${tt:.0f}B")
    c2.metric("Addressable TAM",        f"${ta:.0f}B")
    c3.metric("Arm Market Share",       f"{tr/tt*100:.2f}%", delta="+0.04pp")
    c4.metric("Addr. Penetration",      f"{tr/ta*100:.2f}%", delta="+0.18pp")
    st.markdown("**TAM vs Actual Royalty by LOB**")
    st.bar_chart({"Total TAM (USD B)":[tam[l]["tam"] for l in lobs_s],
        "Addressable (USD B)":[tam[l]["addr"] for l in lobs_s],
        "Actual Royalty (USD B)":[tam[l]["actual"] for l in lobs_s]}, height=300)
    st.caption("Groups: "+(" | ".join(lobs_s)))
    st.markdown("#### Penetration Table")
    st.dataframe({"LOB":lobs_s,
        "TAM (B)":[tam[l]["tam"] for l in lobs_s],
        "Addr (B)":[tam[l]["addr"] for l in lobs_s],
        "Actual (B)":[tam[l]["actual"] for l in lobs_s],
        "Mkt Share %":[round(tam[l]["actual"]/tam[l]["tam"]*100,3) for l in lobs_s],
        "Penetration %":[round(tam[l]["actual"]/tam[l]["addr"]*100,2) for l in lobs_s],
        "Gap (B)":[round(tam[l]["addr"]-tam[l]["actual"],2) for l in lobs_s]},
        use_container_width=True, hide_index=True)

# ── TAB 4 ─────────────────────────────────────────────────────────────────────
with tab4:
    total_risk = sum(riscv[l]["m"] for l in lobs_s)
    st.error(f"⚠️  RISC-V Revenue at Risk (Active Pipeline): **${total_risk:,.0f}M**")
    cols = st.columns(len(lobs_s))
    for i,l in enumerate(lobs_s):
        cols[i].metric(l, f"${riscv[l]['m']:,.0f}M",
            delta=f"{riscv[l]['pct']:.1f}% exposure", delta_color="inverse")
    ca,cb = st.columns(2)
    with ca:
        st.markdown("**RISC-V Revenue at Risk (USD M)**")
        st.bar_chart({"At Risk (USD M)":[riscv[l]["m"] for l in lobs_s]}, height=250)
        st.caption("Bars: "+(" | ".join(lobs_s)))
    with cb:
        st.markdown("**RISC-V Exposure % Trend (2022→2024) | ⚠️ 15% threshold**")
        t = {l:rv_trend[l] for l in lobs_s}
        t["⚠️ 15% Threshold"] = [15,15,15]
        st.line_chart(t, height=250)
        st.caption("X: 2022 | 2023 | 2024")
    st.dataframe({"LOB":lobs_s,"At Risk (USD M)":[riscv[l]["m"] for l in lobs_s],
        "Exposure %":[riscv[l]["pct"] for l in lobs_s],
        "Status":["⚠️ HIGH" if riscv[l]["pct"]>15 else "✅ Watch" for l in lobs_s]},
        use_container_width=True, hide_index=True)

# ── TAB 5 ─────────────────────────────────────────────────────────────────────
with tab5:
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Expectations Run","47",delta="3 tables")
    c2.metric("Pass Rate","100%",delta="Gate passed ✓")
    c3.metric("Anomaly Rate","0.012%",delta="-0.003pp")
    c4.metric("Last Run","04:18 UTC")
    st.markdown("#### GE Suite Results")
    for q in quality_data:
        with st.expander(f"{'✅' if q['pass'] else '❌'}  {q['table']}  —  {q['records']:,} records · {q['anom']} anomalies · {q['run']} UTC"):
            c1,c2,c3,c4 = st.columns(4)
            c1.metric("Records",f"{q['records']:,}")
            c2.metric("Expectations",str(q["n"]))
            c3.metric("Anomalies",str(q["anom"]))
            c4.metric("Rate",f"{q['rate']:.3f}%")
            st.success("Gate PASSED — Silver ETL proceeded.") if q["pass"] else st.error("Gate FAILED.")
    st.markdown("#### 30-Day Anomaly Rate Trend")
    random.seed(7)
    st.line_chart({"royalty_revenue_raw":[round(max(0,random.gauss(0.012,0.003)),4) for _ in range(30)],
        "design_wins_raw":[round(max(0,random.gauss(0,0.001)),4) for _ in range(30)],
        "⚠️ 0.03% Alert":[0.030]*30}, height=200)
    st.caption("X-axis: last 30 pipeline runs")

st.markdown("---")
st.caption("ARM Market Intelligence · Public Demo · Built by Vibhash — Senior Market Intelligence Analyst, Arm Ltd")
