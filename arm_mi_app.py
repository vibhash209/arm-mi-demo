"""
ARM Market Intelligence Platform — Streamlit Application
Author  : Vibhash | Senior Market Intelligence Analyst, Arm Ltd
Purpose : Executive-facing interactive dashboard for royalty analytics,
          design-win pipeline health, TAM penetration, and RISC-V threat monitoring.
Run     : streamlit run arm_mi_app.py
Requires: streamlit, databricks-sdk, pandas, plotly, sqlalchemy, databricks-sql-connector
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from databricks import sql
import os
from datetime import datetime, date
from functools import lru_cache

# ─────────────────────────────────────────────────────────────────────────────
# Page config & branding
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title  = "ARM Market Intelligence",
    page_icon   = "🔷",
    layout      = "wide",
    initial_sidebar_state = "expanded",
)

ARM_BLUE   = "#00A9CE"
ARM_DARK   = "#1A1A2E"
ARM_ACCENT = "#FF6B35"

st.markdown(f"""
<style>
  [data-testid="stMetricValue"]  {{ font-size: 2.2rem; font-weight: 700; color: {ARM_BLUE}; }}
  [data-testid="stMetricDelta"]  {{ font-size: 1rem; }}
  .stTabs [data-baseweb="tab"]   {{ font-weight: 600; }}
  .kpi-card {{
    background: linear-gradient(135deg, {ARM_DARK}, #16213E);
    border: 1px solid {ARM_BLUE}33;
    border-radius: 12px;
    padding: 1.2rem;
    margin: 0.3rem 0;
  }}
  h1, h2, h3 {{ color: #F0F0F0; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Databricks SQL Connector
# ─────────────────────────────────────────────────────────────────────────────
DATABRICKS_HOST  = os.getenv("DATABRICKS_HOST",  "https://your-workspace.azuredatabricks.net")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "your-pat-token")
HTTP_PATH        = os.getenv("DATABRICKS_HTTP_PATH", "/sql/1.0/warehouses/your-warehouse-id")
CATALOG          = "arm_market_intelligence"

@st.cache_resource
def get_connection():
    return sql.connect(
        server_hostname = DATABRICKS_HOST.replace("https://", ""),
        http_path       = HTTP_PATH,
        access_token    = DATABRICKS_TOKEN,
        catalog         = CATALOG,
    )

@st.cache_data(ttl=3600, show_spinner="Fetching data from Databricks…")
def query(sql_str: str) -> pd.DataFrame:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql_str)
    cols = [d[0] for d in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    return pd.DataFrame(rows, columns=cols)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar — Global filters
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/77/Arm_logo_2017.svg", width=120)
    st.markdown("### 🎛️ Filters")

    lob_options = ["All", "Mobile", "IoT", "Automotive", "Infrastructure"]
    selected_lob = st.selectbox("Line of Business", lob_options)

    current_year = datetime.now().year
    year_range   = st.slider(
        "Fiscal Year Range",
        min_value  = current_year - 5,
        max_value  = current_year + 2,
        value      = (current_year - 2, current_year),
    )

    scenario_options = ["Base", "Bull", "Bear"]
    selected_scenario = st.radio("TAM Scenario", scenario_options, horizontal=True)

    st.markdown("---")
    st.caption(f"Data as of: {date.today().strftime('%d %b %Y')}")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# Dynamic SQL helpers (apply sidebar filters)
# ─────────────────────────────────────────────────────────────────────────────
lob_filter   = f"AND line_of_business = '{selected_lob}'" if selected_lob != "All" else ""
year_filter  = f"AND fiscal_year BETWEEN {year_range[0]} AND {year_range[1]}"
year_filter2 = f"AND dw_year     BETWEEN {year_range[0]} AND {year_range[1]}"


# ─────────────────────────────────────────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 8])
with col_title:
    st.markdown("# 🔷 ARM Market Intelligence Platform")
    st.markdown(
        f"**Semiconductor Royalty Analytics | Design Win Pipeline | TAM Intelligence** "
        f"— LOB: `{selected_lob}` | FY: `{year_range[0]}–{year_range[1]}`"
    )
st.markdown("---")


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Royalty Revenue",
    "🏆 Design Win Pipeline",
    "🌍 TAM & Market Share",
    "🔴 RISC-V Threat",
    "🔧 Data Quality",
])


# =============================================================================
# TAB 1: ROYALTY REVENUE
# =============================================================================
with tab1:
    st.subheader("Royalty Revenue Analytics")

    # KPI Cards row
    kpi_sql = f"""
        SELECT
          ROUND(SUM(total_royalty_usd)/1e6, 1)  AS total_royalty_usd_m,
          ROUND(AVG(yoy_growth_pct), 1)         AS avg_yoy_growth_pct,
          ROUND(AVG(qoq_growth_pct), 1)         AS avg_qoq_growth_pct,
          MAX(active_licensees)                 AS peak_licensees,
          ROUND(AVG(v9_share_pct), 1)           AS avg_v9_share_pct
        FROM semantic.royalty_revenue_summary
        WHERE 1=1 {lob_filter} {year_filter}
    """
    kpi_df = query(kpi_sql)

    col1, col2, col3, col4, col5 = st.columns(5)
    if not kpi_df.empty:
        r = kpi_df.iloc[0]
        col1.metric("Total Royalty Revenue",    f"${r['total_royalty_usd_m']:.0f}M")
        col2.metric("Avg YoY Growth",           f"{r['avg_yoy_growth_pct']:.1f}%",
                    delta=f"{r['avg_yoy_growth_pct']:.1f}%")
        col3.metric("Avg QoQ Growth",           f"{r['avg_qoq_growth_pct']:.1f}%",
                    delta=f"{r['avg_qoq_growth_pct']:.1f}%")
        col4.metric("Peak Active Licensees",    f"{int(r['peak_licensees'])}")
        col5.metric("v9 Architecture Share",    f"{r['avg_v9_share_pct']:.1f}%",
                    delta="↑ Modernising")

    st.markdown("---")

    # Quarterly trend line chart
    trend_sql = f"""
        SELECT period_label, line_of_business,
               ROUND(total_royalty_usd/1e6,2) AS royalty_usd_m,
               ROUND(yoy_growth_pct,1) AS yoy_pct,
               ROUND(v9_share_pct,1)  AS v9_pct,
               active_licensees
        FROM semantic.royalty_revenue_summary
        WHERE 1=1 {lob_filter} {year_filter}
        ORDER BY fiscal_year, fiscal_quarter
    """
    trend_df = query(trend_sql)

    if not trend_df.empty:
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig = px.line(
                trend_df, x="period_label", y="royalty_usd_m",
                color="line_of_business",
                title="Quarterly Royalty Revenue by LOB (USD M)",
                labels={"royalty_usd_m": "Revenue USD M", "period_label": "Quarter"},
                template="plotly_dark",
                markers=True,
            )
            fig.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
                              font_color="white", legend_title="LOB")
            st.plotly_chart(fig, use_container_width=True)

        with col_chart2:
            fig2 = px.bar(
                trend_df, x="period_label", y="yoy_pct",
                color="line_of_business",
                title="YoY Revenue Growth % by Quarter",
                barmode="group",
                template="plotly_dark",
            )
            fig2.add_hline(y=0, line_dash="dash", line_color="gray")
            fig2.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
                               font_color="white")
            st.plotly_chart(fig2, use_container_width=True)

    # Architecture mix
    arch_sql = f"""
        SELECT period_label, fiscal_year, fiscal_quarter,
               SUM(v9_royalty_usd)/1e6 AS v9_m,
               SUM(v8_royalty_usd)/1e6 AS v8_m,
               SUM(v7_royalty_usd)/1e6 AS v7_m
        FROM semantic.royalty_revenue_summary
        WHERE 1=1 {lob_filter} {year_filter}
        GROUP BY 1,2,3
        ORDER BY fiscal_year, fiscal_quarter
    """
    arch_df = query(arch_sql)
    if not arch_df.empty:
        fig3 = go.Figure()
        for arch, color in [("v9_m", ARM_BLUE), ("v8_m", "#48CAE4"), ("v7_m", "#90E0EF")]:
            fig3.add_trace(go.Bar(
                name=arch.replace("_m", "").upper(),
                x=arch_df["period_label"],
                y=arch_df[arch],
                marker_color=color,
            ))
        fig3.update_layout(
            barmode="stack",
            title="Architecture Mix — v7 / v8 / v9 Revenue Contribution",
            template="plotly_dark",
            plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
            font_color="white",
        )
        st.plotly_chart(fig3, use_container_width=True)


# =============================================================================
# TAB 2: DESIGN WIN PIPELINE
# =============================================================================
with tab2:
    st.subheader("Design Win Pipeline Health")

    dw_sql = f"""
        SELECT line_of_business, pipeline_stage, competitor_category,
               SUM(deal_count)                          AS deals,
               ROUND(SUM(risk_adj_pipeline_usd)/1e6,1)  AS risk_adj_usd_m,
               ROUND(SUM(gross_pipeline_usd)/1e6,1)     AS gross_usd_m,
               ROUND(AVG(avg_win_prob_pct),1)           AS avg_win_prob,
               ROUND(AVG(win_rate_pct),1)               AS win_rate
        FROM semantic.design_win_pipeline_health
        WHERE 1=1 {lob_filter} {year_filter2}
        GROUP BY 1,2,3
    """
    dw_df = query(dw_sql)

    if not dw_df.empty:
        # Funnel KPIs
        won_df = dw_df[dw_df["pipeline_stage"] == "Closed Won"]
        pipe_df= dw_df[dw_df["pipeline_stage"] == "Active Pipeline"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Won Deals",         f"{int(won_df['deals'].sum())}")
        c2.metric("Won Revenue",        f"${won_df['risk_adj_usd_m'].sum():.0f}M")
        c3.metric("Active Pipeline",    f"${pipe_df['gross_usd_m'].sum():.0f}M (gross)")
        c4.metric("Risk-Adj Pipeline",  f"${pipe_df['risk_adj_usd_m'].sum():.0f}M")

        col_a, col_b = st.columns(2)

        with col_a:
            fig_funnel = px.bar(
                dw_df.groupby(["line_of_business","pipeline_stage"], as_index=False)
                     .agg(risk_adj_usd_m=("risk_adj_usd_m","sum")),
                x="line_of_business", y="risk_adj_usd_m",
                color="pipeline_stage", barmode="group",
                title="Risk-Adjusted Pipeline Value by LOB & Stage",
                template="plotly_dark",
            )
            fig_funnel.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
                                     font_color="white")
            st.plotly_chart(fig_funnel, use_container_width=True)

        with col_b:
            comp_data = (
                dw_df.groupby("competitor_category", as_index=False)
                     .agg(risk_adj_usd_m=("risk_adj_usd_m","sum"),
                          deals=("deals","sum"))
            )
            fig_comp = px.pie(
                comp_data, values="risk_adj_usd_m", names="competitor_category",
                title="Pipeline Risk-Adj Revenue by Competitor",
                template="plotly_dark",
                color_discrete_sequence=px.colors.sequential.Blues_r,
                hole=0.4,
            )
            fig_comp.update_layout(paper_bgcolor="#0E1117", font_color="white")
            st.plotly_chart(fig_comp, use_container_width=True)

        st.markdown("#### Deal Table")
        st.dataframe(
            dw_df.sort_values("risk_adj_usd_m", ascending=False),
            use_container_width=True,
            hide_index=True,
        )


# =============================================================================
# TAB 3: TAM & MARKET SHARE
# =============================================================================
with tab3:
    st.subheader("TAM vs Actual — Market Penetration Analysis")

    tam_sql = f"""
        SELECT line_of_business, fiscal_year, scenario,
               ROUND(tam_usd_bn,2)                    AS tam_usd_bn,
               ROUND(arm_addressable_usd_bn,2)        AS addressable_usd_bn,
               ROUND(actual_royalty_usd_bn,3)         AS actual_royalty_usd_bn,
               ROUND(arm_market_share_pct,2)          AS market_share_pct,
               ROUND(addressable_penetration_pct,2)   AS penetration_pct,
               ROUND(revenue_opportunity_usd_bn,2)    AS opportunity_usd_bn
        FROM semantic.tam_penetration
        WHERE scenario = '{selected_scenario}'
          {lob_filter}
          AND fiscal_year BETWEEN {year_range[0]} AND {year_range[1]+2}
        ORDER BY fiscal_year, line_of_business
    """
    tam_df = query(tam_sql)

    if not tam_df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total TAM (Base, Latest)",
                  f"${tam_df[tam_df['fiscal_year']==tam_df['fiscal_year'].max()]['tam_usd_bn'].sum():.1f}B")
        c2.metric("Avg Market Share",
                  f"{tam_df['market_share_pct'].mean():.2f}%")
        c3.metric("Revenue Opportunity",
                  f"${tam_df['opportunity_usd_bn'].sum():.1f}B",
                  delta="Addressable gap")

        fig_tam = go.Figure()
        for lob in tam_df["line_of_business"].unique():
            sub = tam_df[tam_df["line_of_business"] == lob]
            fig_tam.add_trace(go.Bar(
                name=f"{lob} — TAM",
                x=sub["fiscal_year"].astype(str),
                y=sub["tam_usd_bn"],
                opacity=0.4,
            ))
            fig_tam.add_trace(go.Scatter(
                name=f"{lob} — Actual",
                x=sub["fiscal_year"].astype(str),
                y=sub["actual_royalty_usd_bn"],
                mode="lines+markers",
                line=dict(width=2),
            ))

        fig_tam.update_layout(
            title=f"TAM vs Arm Royalty Revenue by LOB ({selected_scenario} scenario)",
            yaxis_title="USD Billion",
            barmode="group",
            template="plotly_dark",
            plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
            font_color="white",
        )
        st.plotly_chart(fig_tam, use_container_width=True)

        st.markdown("#### Market Share & Penetration Table")
        st.dataframe(
            tam_df.style.background_gradient(
                subset=["market_share_pct","penetration_pct"], cmap="Blues"
            ),
            use_container_width=True,
            hide_index=True,
        )


# =============================================================================
# TAB 4: RISC-V COMPETITIVE THREAT
# =============================================================================
with tab4:
    st.subheader("🔴 RISC-V Competitive Threat Monitor")
    st.info(
        "RISC-V represents the primary open-ISA competitive threat to Arm. "
        "This view tracks revenue at risk across the active design-win pipeline.",
        icon="⚠️"
    )

    riscv_sql = f"""
        SELECT line_of_business, dw_year,
               ROUND(SUM(riscv_revenue_at_risk_usd)/1e6,1) AS riscv_at_risk_usd_m,
               ROUND(AVG(riscv_exposure_pct),1)            AS riscv_exposure_pct,
               SUM(deal_count)                             AS total_deals,
               SUM(CASE WHEN competitor_category='RISC-V' THEN deal_count ELSE 0 END)
                                                           AS riscv_deals
        FROM semantic.design_win_pipeline_health
        WHERE pipeline_stage = 'Active Pipeline'
          {lob_filter} {year_filter2}
        GROUP BY 1,2
        ORDER BY riscv_at_risk_usd_m DESC
    """
    rv_df = query(riscv_sql)

    if not rv_df.empty:
        total_risk = rv_df["riscv_at_risk_usd_m"].sum()
        st.error(f"⚠️  Total RISC-V Revenue at Risk (Active Pipeline): **${total_risk:.0f}M**")

        col1, col2 = st.columns(2)
        with col1:
            fig_rv = px.bar(
                rv_df, x="line_of_business", y="riscv_at_risk_usd_m",
                color="dw_year", title="RISC-V Revenue at Risk by LOB (USD M)",
                template="plotly_dark",
                color_continuous_scale="Reds",
            )
            fig_rv.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
                                 font_color="white")
            st.plotly_chart(fig_rv, use_container_width=True)

        with col2:
            fig_exp = px.line(
                rv_df.sort_values("dw_year"),
                x="dw_year", y="riscv_exposure_pct",
                color="line_of_business",
                title="RISC-V Exposure % Trend by LOB",
                template="plotly_dark",
                markers=True,
            )
            fig_exp.add_hline(y=15, line_dash="dash",
                              annotation_text="15% Alert Threshold",
                              line_color=ARM_ACCENT)
            fig_exp.update_layout(plot_bgcolor="#0E1117", paper_bgcolor="#0E1117",
                                  font_color="white")
            st.plotly_chart(fig_exp, use_container_width=True)

        st.dataframe(
            rv_df.assign(
                riscv_deal_rate_pct=lambda x: round(x["riscv_deals"]/x["total_deals"]*100, 1)
            ),
            use_container_width=True,
            hide_index=True,
        )


# =============================================================================
# TAB 5: DATA QUALITY
# =============================================================================
with tab5:
    st.subheader("🔧 Data Quality & Pipeline Health")

    freshness_sql = """
        SELECT 'royalty_revenue' AS table_name,
               MAX(_silver_ts)   AS last_refreshed,
               COUNT(*)          AS record_count,
               SUM(CASE WHEN _flag_negative_royalty THEN 1 ELSE 0 END) AS anomaly_count
        FROM silver.royalty_revenue
        UNION ALL
        SELECT 'design_wins',
               MAX(_silver_ts), COUNT(*),
               SUM(CASE WHEN probability_pct < 0 OR probability_pct > 100 THEN 1 ELSE 0 END)
        FROM silver.design_wins
    """
    quality_df = query(freshness_sql)

    if not quality_df.empty:
        quality_df["anomaly_rate_pct"] = round(
            quality_df["anomaly_count"] / quality_df["record_count"] * 100, 3
        )
        for _, row in quality_df.iterrows():
            status = "✅" if row["anomaly_rate_pct"] < 1 else "⚠️"
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(f"{status} {row['table_name']}", "Table")
            col2.metric("Records",        f"{int(row['record_count']):,}")
            col3.metric("Anomalies",      f"{int(row['anomaly_count']):,}")
            col4.metric("Anomaly Rate",   f"{row['anomaly_rate_pct']:.3f}%")
        
        st.markdown("---")
        st.caption(f"Last data quality check run: {date.today().strftime('%d %b %Y')}")
        st.caption("Quality gate powered by **Great Expectations** | Orchestrated via **Databricks Workflows**")


# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "ARM Market Intelligence Platform · "
    "Built on Databricks Delta Lake + Unity Catalog · "
    "Semantic layer via Databricks SQL · "
    "Visualisation: Streamlit + Plotly"
)
