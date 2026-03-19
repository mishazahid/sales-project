"""
Phase 4: Streamlit Dashboard
AI Sales Acceleration Engine - Interactive Dashboard
"""
import os
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Page configuration
st.set_page_config(
    page_title="AI Sales Acceleration Engine",
    page_icon="ASE",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL – override with API_BASE_URL env var in hosted deployments
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        color: #0f172a;
        margin-bottom: 0.75rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #64748b;
        margin-bottom: 1.25rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #0f172a, #1d4ed8);
        padding: 1rem 1.1rem;
        border-radius: 0.75rem;
        color: #f9fafb;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.35);
    }
    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #e5e7eb;
        margin-bottom: 0.25rem;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: 600;
    }
    .metric-caption {
        font-size: 0.75rem;
        color: #cbd5f5;
        margin-top: 0.15rem;
    }
    .section-card {
        background-color: #ffffff;
        border-radius: 0.75rem;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
        border: 1px solid #e5e7eb;
        margin-bottom: 1.5rem;
    }
    .section-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 0.75rem;
    }
    .section-description {
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 0.75rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 0.35rem;
        padding-bottom: 0.35rem;
    }
    .stAlert {
        padding: 0.75rem 1rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load data files."""
    try:
        crm_leads = pd.read_csv("data/crm_leads.csv")
        email_engagement = pd.read_csv("data/email_engagement.csv")
        call_transcripts = pd.read_csv("data/call_transcripts.csv")
        revenue_history = pd.read_csv("data/revenue_history.csv")
        return crm_leads, email_engagement, call_transcripts, revenue_history
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None


def check_api_connection():
    """Check if API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def call_api(endpoint, method="GET", data=None):
    """Make API call."""
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=60)
        else:
            response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {e}. Make sure the API server is running at {API_BASE_URL}")
        return None


def main():
    """Main dashboard application."""
    
    # Header
    st.markdown('<div class="main-header">AI Sales Acceleration Engine</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Integrated demo for lead scoring, outreach personalization, and call intelligence on synthetic sales data.</div>',
        unsafe_allow_html=True,
    )
    
    # Check API connection
    api_connected = check_api_connection()
    if not api_connected:
        st.warning("API server not connected. Please start the API server: `uvicorn api.main:app --reload`")
        st.info("Dashboard will work in offline mode with limited functionality.")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        [
            "Sales Overview",
            "Lead Scoring",
            "Email Generator",
            "Call Intelligence",
            "Rep Performance",
            "AI Copilot",
        ],
    )
    
    # Load data
    crm_leads, email_engagement, call_transcripts, revenue_history = load_data()
    
    if crm_leads is None:
        st.error("Could not load data files. Please run `python generate_synthetic_data.py` first.")
        return
    
    # Route to appropriate page
    if page == "Sales Overview":
        show_sales_overview(crm_leads, email_engagement, revenue_history, api_connected)
    elif page == "Lead Scoring":
        show_lead_scoring(crm_leads, email_engagement, api_connected)
    elif page == "Email Generator":
        show_email_generator(crm_leads, api_connected)
    elif page == "Call Intelligence":
        show_call_intelligence(call_transcripts, api_connected)
    elif page == "Rep Performance":
        show_rep_performance(crm_leads, email_engagement, call_transcripts)
    elif page == "AI Copilot":
        show_ai_copilot(crm_leads, email_engagement, api_connected)


def show_rep_performance(crm_leads, email_engagement, call_transcripts):
    """Rep performance analytics dashboard."""
    st.header("Rep Performance Analytics")
    st.markdown(
        '<div class="sub-header">Compare reps across owned pipeline, win rates, email engagement, and call outcomes.</div>',
        unsafe_allow_html=True,
    )

    if crm_leads is None or email_engagement is None or call_transcripts is None:
        st.error("Required data not available. Please ensure synthetic data has been generated.")
        return

    # Define synthetic sales reps (Account Executives)
    reps = [
        {"id": 1, "name": "AE 1 - Jordan Lee"},
        {"id": 2, "name": "AE 2 - Alex Patel"},
        {"id": 3, "name": "AE 3 - Morgan Chen"},
        {"id": 4, "name": "AE 4 - Taylor Alvarez"},
        {"id": 5, "name": "AE 5 - Casey Robinson"},
        {"id": 6, "name": "AE 6 - Riley Brooks"},
    ]

    # Deterministic assignment of leads to reps based on lead_id
    leads_rep = crm_leads.copy()
    leads_rep["rep_id"] = leads_rep["lead_id"].apply(lambda x: (int(x) % len(reps)) + 1)
    rep_map = {r["id"]: r["name"] for r in reps}
    leads_rep["rep_name"] = leads_rep["rep_id"].map(rep_map)

    # Email activity joined to reps
    emails_rep = email_engagement.merge(
        leads_rep[["lead_id", "rep_id", "rep_name"]],
        on="lead_id",
        how="left",
    )

    # Call activity joined to reps
    calls_rep = call_transcripts.merge(
        leads_rep[["lead_id", "rep_id", "rep_name"]],
        on="lead_id",
        how="left",
    )

    # High-level per-rep KPIs
    leads_rep["is_open"] = ~leads_rep["status"].isin(["Closed Won", "Closed Lost"])

    rep_lead_kpis = (
        leads_rep.groupby(["rep_id", "rep_name"])
        .agg(
            total_leads=("lead_id", "nunique"),
            open_leads=("is_open", "sum"),
            won_deals=("status", lambda s: (s == "Closed Won").sum()),
            lost_deals=("status", lambda s: (s == "Closed Lost").sum()),
            pipeline_value_open=("estimated_deal_size", lambda s: s[leads_rep.loc[s.index, "is_open"]].sum()),
            avg_baseline_score=("lead_score_baseline", "mean"),
        )
        .reset_index()
    )

    rep_lead_kpis["win_rate"] = rep_lead_kpis.apply(
        lambda row: (row["won_deals"] / row["total_leads"] * 100) if row["total_leads"] > 0 else 0,
        axis=1,
    )

    # Email KPIs per rep
    rep_email_kpis = (
        emails_rep.groupby(["rep_id", "rep_name"])
        .agg(
            emails_sent=("email_sequence_step", "count"),
            opens=("opened", "sum"),
            clicks=("clicked", "sum"),
            replies=("replied", "sum"),
        )
        .reset_index()
    )

    rep_email_kpis["open_rate"] = rep_email_kpis.apply(
        lambda row: (row["opens"] / row["emails_sent"] * 100) if row["emails_sent"] > 0 else 0,
        axis=1,
    )
    rep_email_kpis["reply_rate"] = rep_email_kpis.apply(
        lambda row: (row["replies"] / row["emails_sent"] * 100) if row["emails_sent"] > 0 else 0,
        axis=1,
    )

    # Call KPIs per rep
    rep_call_kpis = (
        calls_rep.groupby(["rep_id", "rep_name"])
        .agg(
            calls_made=("call_id", "nunique"),
            avg_call_duration=("duration_minutes", "mean"),
        )
        .reset_index()
    )

    # Sentiment distribution per rep (flattened)
    sentiment_dist = (
        calls_rep.groupby(["rep_id", "rep_name", "sentiment"])
        .agg(count=("call_id", "nunique"))
        .reset_index()
    )

    # Merge KPIs into a single frame for table view
    rep_summary = (
        rep_lead_kpis.merge(rep_email_kpis, on=["rep_id", "rep_name"], how="left")
        .merge(rep_call_kpis, on=["rep_id", "rep_name"], how="left")
        .fillna(0)
    )

    # Filter for rep
    rep_names = [r["name"] for r in reps]
    selected_rep_name = st.selectbox(
        "Select rep", options=["All reps"] + rep_names, key="rp_rep_select"
    )

    if selected_rep_name != "All reps":
        rep_summary_view = rep_summary[rep_summary["rep_name"] == selected_rep_name]
    else:
        rep_summary_view = rep_summary

    # Top-level metrics (aggregate over selection)
    total_leads_sel = int(rep_summary_view["total_leads"].sum())
    open_leads_sel = int(rep_summary_view["open_leads"].sum())
    won_deals_sel = int(rep_summary_view["won_deals"].sum())
    pipeline_value_sel = float(rep_summary_view["pipeline_value_open"].sum())

    tab_summary, tab_table, tab_charts = st.tabs(["Summary", "Table", "Charts"])

    with tab_summary:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Selection Summary</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-description">Aggregate KPIs for the selected rep (or all reps), derived from synthetic CRM, email, and call data.</div>',
            unsafe_allow_html=True,
        )
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                  <div class="metric-label">Total Leads</div>
                  <div class="metric-value">{total_leads_sel:,}</div>
                  <div class="metric-caption">Owned by selection</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                f"""
                <div class="metric-card">
                  <div class="metric-label">Open Pipeline</div>
                  <div class="metric-value">{open_leads_sel:,}</div>
                  <div class="metric-caption">Non-closed opportunities</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                f"""
                <div class="metric-card">
                  <div class="metric-label">Won Deals</div>
                  <div class="metric-value">{won_deals_sel:,}</div>
                  <div class="metric-caption">Closed-won deals</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                f"""
                <div class="metric-card">
                  <div class="metric-label">Open Pipeline Value</div>
                  <div class="metric-value">${pipeline_value_sel:,.0f}</div>
                  <div class="metric-caption">Estimated deal size</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_table:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Per-Rep Performance Table</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-description">One row per rep with pipeline and activity indicators. Sort and filter to explore patterns.</div>',
            unsafe_allow_html=True,
        )
        display_cols = [
            "rep_name",
            "total_leads",
            "open_leads",
            "won_deals",
            "lost_deals",
            "win_rate",
            "pipeline_value_open",
            "avg_baseline_score",
            "emails_sent",
            "open_rate",
            "reply_rate",
            "calls_made",
            "avg_call_duration",
        ]
        st.dataframe(
            rep_summary_view[display_cols].rename(columns={"rep_name": "Rep"}),
            use_container_width=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_charts:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Performance Charts</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-description">Quick comparisons across reps for win rates, email engagement, and call sentiment.</div>',
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Win Rate by Rep")
            fig_win = px.bar(
                rep_summary,
                x="rep_name",
                y="win_rate",
                labels={"rep_name": "Rep", "win_rate": "Win Rate (%)"},
                title=None,
            )
            fig_win.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            fig_win.update_xaxes(tickangle=45)
            st.plotly_chart(fig_win, use_container_width=True)

        with col2:
            st.subheader("Email Open Rate by Rep")
            fig_email = px.bar(
                rep_summary,
                x="rep_name",
                y="open_rate",
                labels={"rep_name": "Rep", "open_rate": "Open Rate (%)"},
                title=None,
            )
            fig_email.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            fig_email.update_xaxes(tickangle=45)
            st.plotly_chart(fig_email, use_container_width=True)

        st.subheader("Call Sentiment by Rep")
        if not sentiment_dist.empty:
            fig_sentiment = px.bar(
                sentiment_dist,
                x="rep_name",
                y="count",
                color="sentiment",
                barmode="stack",
                labels={"rep_name": "Rep", "count": "Calls", "sentiment": "Sentiment"},
                title=None,
            )
            fig_sentiment.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            fig_sentiment.update_xaxes(tickangle=45)
            st.plotly_chart(fig_sentiment, use_container_width=True)
        else:
            st.info("No call data available to display sentiment distribution.")

        st.markdown("</div>", unsafe_allow_html=True)




def show_sales_overview(crm_leads, email_engagement, revenue_history, api_connected):
    """Sales overview dashboard."""
    st.header("Sales Overview & AI Forecast")
    
    # Key Metrics Row (hero cards)
    total_leads = len(crm_leads)
    qualified_leads = len(
        crm_leads[
            crm_leads["status"].isin(
                ["Qualified", "Demo Scheduled", "Proposal Sent", "Negotiation"]
            )
        ]
    )
    converted_leads = len(crm_leads[crm_leads["converted"] == 1])
    conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
              <div class="metric-label">Total Leads</div>
              <div class="metric-value">{total_leads:,}</div>
              <div class="metric-caption">All active records in CRM</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
              <div class="metric-label">Qualified Pipeline</div>
              <div class="metric-value">{qualified_leads:,}</div>
              <div class="metric-caption">Qualified through to negotiation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
              <div class="metric-label">Closed Won</div>
              <div class="metric-value">{converted_leads:,}</div>
              <div class="metric-caption">Synthetic historical wins</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"""
            <div class="metric-card">
              <div class="metric-label">Conversion Rate</div>
              <div class="metric-value">{conversion_rate:.1f}%</div>
              <div class="metric-caption">Won / total leads</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    st.markdown("")
    
    # Charts Row in section cards
    col1, col2 = st.columns((1.1, 1))
    
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Lead Status Distribution</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-description">Mix of new, qualified, proposal, and closed opportunities across the synthetic pipeline.</div>',
            unsafe_allow_html=True,
        )
        status_counts = crm_leads["status"].value_counts()
        fig_status = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title=None,
        )
        fig_status.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_status, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Leads by Source</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-description">Relative contribution of web, events, and outbound to top-of-funnel volume.</div>',
            unsafe_allow_html=True,
        )
        source_counts = crm_leads["lead_source"].value_counts()
        fig_source = px.bar(
            x=source_counts.index,
            y=source_counts.values,
            title=None,
            labels={"x": "Source", "y": "Count"},
        )
        fig_source.update_layout(margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_source, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Revenue Forecast
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Revenue History & Forecast</div>', unsafe_allow_html=True)
    
    if revenue_history is not None and len(revenue_history) > 0:
        revenue_history['month'] = pd.to_datetime(revenue_history['month'])
        revenue_history = revenue_history.sort_values('month')
        
        fig_revenue = go.Figure()
        
        # Historical data
        fig_revenue.add_trace(go.Scatter(
            x=revenue_history['month'],
            y=revenue_history['mrr'],
            mode='lines+markers',
            name='MRR',
            line=dict(color='#1f77b4', width=3)
        ))
        
        # Forecast (simple projection)
        if len(revenue_history) > 6:
            last_month = revenue_history['month'].iloc[-1]
            last_mrr = revenue_history['mrr'].iloc[-1]
            growth_rate = (revenue_history['mrr'].iloc[-1] / revenue_history['mrr'].iloc[-6] - 1) / 6
            
            forecast_months = pd.date_range(start=last_month + pd.DateOffset(months=1), periods=6, freq='M')
            forecast_mrr = [last_mrr * (1 + growth_rate) ** (i+1) for i in range(6)]
            
            fig_revenue.add_trace(go.Scatter(
                x=forecast_months,
                y=forecast_mrr,
                mode='lines+markers',
                name='AI Forecast',
                line=dict(color='#ff7f0e', width=2, dash='dash')
            ))
        
        fig_revenue.update_layout(
            title="Monthly Recurring Revenue (MRR) - Historical & Forecast",
            xaxis_title="Month",
            yaxis_title="MRR ($)",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    # Email Engagement Metrics
    st.subheader("Email Engagement Metrics")
    
    if email_engagement is not None:
        email_engagement["sent_at"] = pd.to_datetime(email_engagement["sent_at"])
        view_choice = st.radio(
            "View as",
            ["Summary metrics", "Time series"],
            horizontal=True,
        )

        if view_choice == "Summary metrics":
            col1, col2, col3 = st.columns(3)

            total_emails = len(email_engagement)
            total_opens = email_engagement["opened"].sum()
            total_clicks = email_engagement["clicked"].sum()
            total_replies = email_engagement["replied"].sum()

            open_rate = (total_opens / total_emails * 100) if total_emails > 0 else 0
            click_rate = (total_clicks / total_opens * 100) if total_opens > 0 else 0
            reply_rate = (total_replies / total_emails * 100) if total_emails > 0 else 0

            with col1:
                st.metric("Open Rate", f"{open_rate:.1f}%")
            with col2:
                st.metric("Click-to-Open Rate", f"{click_rate:.1f}%")
            with col3:
                st.metric("Reply Rate", f"{reply_rate:.1f}%")
        else:
            email_daily = (
                email_engagement.groupby(email_engagement["sent_at"].dt.date)
                .agg({"opened": "sum", "clicked": "sum", "replied": "sum"})
                .reset_index()
            )
            email_daily.columns = ["date", "opens", "clicks", "replies"]

            fig_email = go.Figure()
            fig_email.add_trace(
                go.Scatter(
                    x=email_daily["date"],
                    y=email_daily["opens"],
                    name="Opens",
                    mode="lines+markers",
                )
            )
            fig_email.add_trace(
                go.Scatter(
                    x=email_daily["date"],
                    y=email_daily["clicks"],
                    name="Clicks",
                    mode="lines+markers",
                )
            )
            fig_email.add_trace(
                go.Scatter(
                    x=email_daily["date"],
                    y=email_daily["replies"],
                    name="Replies",
                    mode="lines+markers",
                )
            )

            fig_email.update_layout(
                title="Email Engagement Over Time",
                xaxis_title="Date",
                yaxis_title="Count",
                hovermode="x unified",
            )

            st.plotly_chart(fig_email, use_container_width=True)


def show_lead_scoring(crm_leads, email_engagement, api_connected):
    """Lead scoring interface."""
    st.header("Predictive Lead Scoring")
    st.markdown(
        '<div class="sub-header">Train the scoring model, inspect ranked leads, and drill into a single record.</div>',
        unsafe_allow_html=True,
    )
    
    tab_train, tab_ranked, tab_drill = st.tabs(["Model Training", "Ranked Leads", "Lead Drilldown"])

    with tab_train:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Model Training</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-description">Train or retrain the lead scoring model on the synthetic CRM + engagement history.</div>',
            unsafe_allow_html=True,
        )
        if st.button("Train Model", type="primary"):
            if api_connected:
                with st.spinner("Training model... This may take a few minutes."):
                    result = call_api("/api/leads/train", method="POST")
                    if result:
                        st.success("Model trained successfully.")
            else:
                st.warning("API not connected. Cannot train model.")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_ranked:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Top Priority Leads</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-description">View a ranked list of leads and a quick visualization of the top 10.</div>',
            unsafe_allow_html=True,
        )

        num_leads = st.slider("Number of leads to display", 10, 100, 20, key="ls_num_leads")

        if api_connected:
            if st.button("Refresh Lead Scores", type="primary"):
                with st.spinner("Scoring leads..."):
                    result = call_api(f"/api/leads/top?limit={num_leads}")
                    if result:
                        top_leads_df = pd.DataFrame(result)
                        st.dataframe(top_leads_df, use_container_width=True)

                        if len(top_leads_df) > 0:
                            fig = px.bar(
                                top_leads_df.head(10),
                                x="company",
                                y="conversion_probability",
                                title=None,
                                labels={
                                    "conversion_probability": "Conversion Probability",
                                    "company": "Company",
                                },
                            )
                            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
                            fig.update_xaxes(tickangle=45)
                            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Using baseline scores (API not connected). Connect API for AI-powered scoring.")

            scored_leads = crm_leads.copy()
            scored_leads["conversion_probability"] = scored_leads["lead_score_baseline"] / 100
            scored_leads["priority_rank"] = (
                scored_leads["conversion_probability"].rank(ascending=False).astype(int)
            )

            top_leads = scored_leads.nlargest(num_leads, "conversion_probability")[
                [
                    "lead_id",
                    "company",
                    "first_name",
                    "last_name",
                    "status",
                    "conversion_probability",
                    "priority_rank",
                ]
            ]

            st.dataframe(top_leads, use_container_width=True)

            fig = px.bar(
                top_leads.head(10),
                x="company",
                y="conversion_probability",
                title=None,
                labels={"conversion_probability": "Conversion Probability", "company": "Company"},
            )
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with tab_drill:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Search & Score an Individual Lead</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-description">Inspect a single lead and request an AI score (or view the baseline score if offline).</div>',
            unsafe_allow_html=True,
        )

        lead_search = st.selectbox(
            "Select a lead",
            options=crm_leads["lead_id"].tolist(),
            format_func=lambda x: f"Lead {x} - {crm_leads[crm_leads['lead_id'] == x]['company'].iloc[0]}",
            key="ls_lead_select",
        )

        if lead_search:
            lead_data = crm_leads[crm_leads["lead_id"] == lead_search].iloc[0]

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Lead Information:**")
                st.write(f"**Name:** {lead_data['first_name']} {lead_data['last_name']}")
                st.write(f"**Company:** {lead_data['company']}")
                st.write(f"**Job Title:** {lead_data['job_title']}")
                st.write(f"**Industry:** {lead_data['industry']}")
                st.write(f"**Status:** {lead_data['status']}")

            with col2:
                if api_connected:
                    if st.button("Get AI Score", type="primary"):
                        with st.spinner("Scoring lead..."):
                            result = call_api(
                                "/api/leads/score",
                                method="POST",
                                data={"lead_ids": [int(lead_search)]},
                            )
                            if result and len(result) > 0:
                                score_data = result[0]
                                st.metric(
                                    "Conversion Probability",
                                    f"{score_data['conversion_probability']:.1%}",
                                )
                                st.metric("Priority Rank", f"#{score_data['priority_rank']}")
                else:
                    st.metric("Baseline Score", f"{lead_data['lead_score_baseline']:.1f}")
                    st.info("Connect API for AI-powered scoring")

        st.markdown("</div>", unsafe_allow_html=True)


def show_email_generator(crm_leads, api_connected):
    """Email generation interface."""
    st.header("AI Email Personalization")
    st.markdown(
        '<div class="sub-header">Use RAG + LLM templates to generate tailored outreach for any lead in the dataset.</div>',
        unsafe_allow_html=True,
    )
    
    tab_single, tab_ab = st.tabs(["Single Email", "A/B Variants"])

    lead_search = st.selectbox(
        "Choose a lead",
        options=crm_leads["lead_id"].tolist(),
        format_func=lambda x: f"Lead {x} - {crm_leads[crm_leads['lead_id'] == x]['company'].iloc[0]}",
        key="eg_lead_select",
    )

    if not lead_search:
        return

    lead_data = crm_leads[crm_leads["lead_id"] == lead_search].iloc[0]

    with tab_single:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Lead Context</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-description">The generator uses role + industry to retrieve relevant product context.</div>',
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        with c1:
            st.write(f"**Name:** {lead_data['first_name']} {lead_data['last_name']}")
            st.write(f"**Company:** {lead_data['company']}")
            st.write(f"**Job Title:** {lead_data['job_title']}")
        with c2:
            st.write(f"**Industry:** {lead_data['industry']}")
            st.write(f"**Company Size:** {lead_data['company_size_bucket']}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Generate Email</div>', unsafe_allow_html=True)
        variant = st.radio("Variant", ["A", "B"], horizontal=True, key="eg_variant")

        if st.button("Generate Personalized Email", type="primary"):
            if api_connected:
                with st.spinner("Generating personalized email..."):
                    result = call_api(
                        "/api/emails/generate",
                        method="POST",
                        data={"lead_id": int(lead_search), "variant": variant},
                    )
                    if result:
                        st.success(
                            f"Email generated (Personalization Score: {result['personalization_score']:.0%})"
                        )
                        st.write(f"**Subject:** {result['subject']}")
                        st.text_area("Email Body", result["body"], height=300, key="eg_body_single")

                        email_text = f"Subject: {result['subject']}\n\n{result['body']}"
                        st.download_button(
                            "Download Email",
                            email_text,
                            file_name=f"email_lead_{lead_search}_variant_{variant}.txt",
                        )
            else:
                st.warning("API not connected. Using template-based generation.")
                from modules.email_personalization import EmailPersonalizationEngine

                engine = EmailPersonalizationEngine()
                lead_dict = lead_data.to_dict()
                email = engine.generate_personalized_email(lead_dict, variant=variant)

                st.success(
                    f"Email generated (Personalization Score: {email['personalization_score']:.0%})"
                )
                st.write(f"**Subject:** {email['subject']}")
                st.text_area("Email Body", email["body"], height=300, key="eg_body_offline")

        st.markdown("</div>", unsafe_allow_html=True)

    with tab_ab:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Generate A/B Variants</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-description">Produce two versions with different structure and messaging focus for testing.</div>',
            unsafe_allow_html=True,
        )

        if st.button("Generate A/B Variants", type="primary"):
            if api_connected:
                with st.spinner("Generating A/B variants..."):
                    result = call_api(
                        "/api/emails/generate-ab",
                        method="POST",
                        data={"lead_id": int(lead_search)},
                    )
                    if result:
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown('<div class="section-title">Variant A</div>', unsafe_allow_html=True)
                            st.write(f"**Subject:** {result['variant_a']['subject']}")
                            st.text_area("Body A", result["variant_a"]["body"], height=260, key="variant_a")

                        with col2:
                            st.markdown('<div class="section-title">Variant B</div>', unsafe_allow_html=True)
                            st.write(f"**Subject:** {result['variant_b']['subject']}")
                            st.text_area("Body B", result["variant_b"]["body"], height=260, key="variant_b")
            else:
                st.warning("API not connected. Please start the API server.")

        st.markdown("</div>", unsafe_allow_html=True)


def show_call_intelligence(call_transcripts, api_connected):
    """Call intelligence interface."""
    st.header("Call Intelligence & Risk Detection")
    st.markdown(
        '<div class="sub-header">Review risk reports and analyze individual calls for sentiment, objections, and next steps.</div>',
        unsafe_allow_html=True,
    )
    
    tab_report, tab_single = st.tabs(["Risk Report", "Call Drilldown"])

    with tab_report:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Risk Analysis Report</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-description">Batch analysis across recent calls to surface risk levels, sentiment, and top objections.</div>',
            unsafe_allow_html=True,
        )

        if api_connected:
            num_calls = st.slider("Number of calls to analyze", 10, 200, 50, key="ci_num_calls")

            if st.button("Generate Risk Report", type="primary"):
                with st.spinner("Analyzing calls..."):
                    result = call_api(f"/api/calls/risk-report?limit={num_calls}")
                    if result:
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Total Calls Analyzed", result["total_calls_analyzed"])
                            st.write("**Risk Distribution:**")
                            for risk, count in result["risk_distribution"].items():
                                st.write(f"- {risk.capitalize()}: {count}")

                        with col2:
                            st.write("**Sentiment Distribution:**")
                            for sentiment, count in result["sentiment_distribution"].items():
                                st.write(f"- {sentiment.capitalize()}: {count}")
                            st.metric(
                                "Avg Sentiment Score",
                                f"{result['average_sentiment_score']:.2f}",
                            )

                        with col3:
                            st.write("**Top Objections:**")
                            for objection, count in list(result["top_objections"].items())[:5]:
                                st.write(f"- {objection}: {count}")
                            st.metric("High-Risk Calls", result["high_risk_calls_count"])
        else:
            st.warning("API not connected. Please start the API server for call analysis.")

        st.markdown("</div>", unsafe_allow_html=True)

    with tab_single:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Analyze an Individual Call</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-description">Select a call transcript, then run AI analysis for summary, sentiment, and suggested next steps.</div>',
            unsafe_allow_html=True,
        )

        if call_transcripts is not None and len(call_transcripts) > 0:
            call_search = st.selectbox(
                "Select a call",
                options=call_transcripts["call_id"].tolist(),
                format_func=lambda x: f"{x} - Lead {call_transcripts[call_transcripts['call_id'] == x]['lead_id'].iloc[0]}",
                key="ci_call_select",
            )

            if call_search:
                call_data = call_transcripts[call_transcripts["call_id"] == call_search].iloc[0]

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown('<div class="section-title">Transcript</div>', unsafe_allow_html=True)
                    st.text_area(
                        "Transcript",
                        call_data["transcript"],
                        height=320,
                        disabled=True,
                        key="ci_transcript",
                    )

                with col2:
                    st.markdown('<div class="section-title">Details</div>', unsafe_allow_html=True)
                    st.write(f"**Duration:** {call_data['duration_minutes']} minutes")
                    st.write(f"**Date:** {call_data['call_date']}")
                    st.write(f"**Lead ID:** {call_data['lead_id']}")

                if api_connected:
                    if st.button("Analyze Call", type="primary"):
                        with st.spinner("Analyzing call transcript..."):
                            call_id_num = call_search.replace("CALL-", "")
                            result = call_api(
                                "/api/calls/analyze",
                                method="POST",
                                data={"call_id": int(call_id_num)},
                            )
                            if result:
                                st.success("Call analyzed successfully.")

                                c1, c2 = st.columns(2)
                                with c1:
                                    st.metric("Sentiment", result["sentiment"].capitalize())
                                    st.metric("Risk Level", result["risk_level"].capitalize())
                                with c2:
                                    st.write("**Objections Detected:**")
                                    for obj in result["objections_detected"]:
                                        st.write(f"- {obj}")

                                st.markdown('<div class="section-title">Summary</div>', unsafe_allow_html=True)
                                st.write(result["summary"])

                                st.markdown('<div class="section-title">Recommended Next Steps</div>', unsafe_allow_html=True)
                                for i, step in enumerate(result["recommended_next_steps"], 1):
                                    st.write(f"{i}. {step}")
                else:
                    st.info("Connect API to analyze calls with AI")

        st.markdown("</div>", unsafe_allow_html=True)


def show_ai_copilot(crm_leads, email_engagement, api_connected):
    """AI sales copilot page: daily suggestions + follow-up simulation."""
    st.header("Daily AI Sales Copilot")
    st.markdown(
        '<div class="sub-header">Get prioritized to-dos and simulate multi-step follow-up plays for any lead.</div>',
        unsafe_allow_html=True,
    )

    if not api_connected:
        st.warning(
            "API server not connected. Start it with `uvicorn api.main:app --reload` "
            "to enable live copilot suggestions and simulations."
        )

    tab_suggest, tab_sim = st.tabs(["Daily Suggestions", "Follow-Up Simulation"])

    with tab_suggest:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Daily Suggestions</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-description">Prioritized actions based on lead score, engagement patterns, and recent call risk indicators.</div>',
            unsafe_allow_html=True,
        )
        if api_connected:
            limit = st.slider("Number of suggestions", 5, 25, 10, key="ac_limit")
            if st.button("Refresh Suggestions", type="primary"):
                with st.spinner("Generating daily copilot suggestions..."):
                    suggestions = call_api(f"/api/copilot/daily-suggestions?limit={limit}")
                    if suggestions:
                        df = pd.DataFrame(suggestions)
                        df_display = df.rename(
                            columns={
                                "suggestion_type": "Type",
                                "lead_id": "Lead ID",
                                "company": "Company",
                                "reason": "Reason",
                                "priority": "Priority",
                                "recommended_action": "Recommended Action",
                            }
                        )
                        st.dataframe(df_display, use_container_width=True)
        else:
            st.info(
                "Copilot suggestions use the API for fresh analysis of leads, emails, and calls. "
                "Start the API server to see live recommendations."
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_sim:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Autonomous Follow-Up Simulation</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-description">Simulate a multi-touch outreach sequence and estimate engagement and conversion lift.</div>',
            unsafe_allow_html=True,
        )

        if crm_leads is not None and len(crm_leads) > 0:
            lead_options = crm_leads["lead_id"].tolist()
            selected_lead = st.selectbox(
                "Lead for simulation",
                options=lead_options,
                format_func=lambda x: f"Lead {x} - {crm_leads[crm_leads['lead_id'] == x]['company'].iloc[0]}",
                key="ac_lead",
            )
        else:
            selected_lead = None

        days = st.slider("Simulation window (days)", 7, 30, 14, key="ac_days")
        steps = st.slider("Number of follow-up steps", 2, 6, 4, key="ac_steps")

        if st.button("Run Simulation", type="primary"):
            if api_connected:
                with st.spinner("Simulating autonomous follow-up sequence..."):
                    payload = {"lead_id": int(selected_lead)} if selected_lead else {}
                    payload.update({"days": int(days), "steps": int(steps)})
                    result = call_api(
                        "/api/copilot/simulate-followup", method="POST", data=payload
                    )
                    if result:
                        st.success("Simulation complete.")

                        c1, c2, c3 = st.columns(3)
                        with c1:
                            st.markdown(
                                f"""
                                <div class="metric-card">
                                  <div class="metric-label">Overall Open Rate</div>
                                  <div class="metric-value">{result['projected_overall_open_rate']*100:.1f}%</div>
                                  <div class="metric-caption">Across the full sequence</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        with c2:
                            st.markdown(
                                f"""
                                <div class="metric-card">
                                  <div class="metric-label">Overall Reply Rate</div>
                                  <div class="metric-value">{result['projected_overall_reply_rate']*100:.1f}%</div>
                                  <div class="metric-caption">Replies over all touches</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        with c3:
                            st.markdown(
                                f"""
                                <div class="metric-card">
                                  <div class="metric-label">Conversion Lift</div>
                                  <div class="metric-value">+{result['projected_conversion_lift']*100:.1f} pts</div>
                                  <div class="metric-caption">Vs. baseline behavior</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                        seq_df = pd.DataFrame(result["sequence"])
                        seq_df_display = seq_df.rename(
                            columns={
                                "step_number": "Step",
                                "channel": "Channel",
                                "suggested_day_offset": "Day Offset",
                                "message_focus": "Message Focus",
                                "expected_open_rate": "Expected Open Rate",
                                "expected_reply_rate": "Expected Reply Rate",
                            }
                        )
                        seq_df_display["Expected Open Rate"] = (
                            seq_df_display["Expected Open Rate"] * 100
                        ).round(1)
                        seq_df_display["Expected Reply Rate"] = (
                            seq_df_display["Expected Reply Rate"] * 100
                        ).round(1)

                        st.subheader("Sequence Plan")
                        st.dataframe(seq_df_display, use_container_width=True)
            else:
                st.info("Start the API server to run simulations.")

        st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

