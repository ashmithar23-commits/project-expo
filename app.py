"""
FlowFix — AI Workflow Bottleneck Detective
College Project Expo Web Application
Tagline: "Find the bottleneck. Fix the flow."
"""

import streamlit as st
import pandas as pd
import numpy as np

# FlowFix modules
from data_generator import generate_historical_orders, generate_live_orders, get_stage_definitions
from analyzer import calculate_stage_metrics, calculate_efficiency_score, simulate_what_if
from visualizations import (
    create_stage_distribution_chart,
    create_stage_share_donut,
    create_before_after_chart,
    create_efficiency_gauge,
    create_live_radar_scatter
)
from recommendations import get_root_cause_catalog, get_recommendation_for_stage

# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="FlowFix — AI Workflow Bottleneck Detective",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling suitable for project expo presentation
st.markdown("""
<style>
    /* Main container and font */
    .main {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Header card */
    .flowfix-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        padding: 24px 30px;
        border-radius: 12px;
        margin-bottom: 22px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .flowfix-title {
        font-size: 28px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .flowfix-tagline {
        font-size: 15px;
        color: #94a3b8;
        margin-top: 6px;
        font-weight: 400;
    }
    .flowfix-badge {
        background-color: #2563eb;
        color: #ffffff;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 8px;
    }
    
    /* Metric Card Styling */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.15s ease-in-out;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #cbd5e1;
    }
    .metric-label {
        font-size: 12px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: #0f172a;
        margin: 4px 0;
    }
    .metric-sub {
        font-size: 12px;
        color: #10b981;
        font-weight: 600;
    }
    .metric-sub-neutral {
        font-size: 12px;
        color: #64748b;
    }
    .metric-sub-alert {
        font-size: 12px;
        color: #ef4444;
        font-weight: 600;
    }
    
    /* Callout & Recommendation boxes */
    .callout-box {
        background-color: #f8fafc;
        border-left: 4px solid #2563eb;
        padding: 16px 20px;
        border-radius: 0 8px 8px 0;
        margin: 15px 0;
    }
    .bottleneck-box {
        background-color: #fff7ed;
        border: 1px solid #fed7aa;
        border-left: 5px solid #ea580c;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 15px 0;
    }
    .success-box {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 5px solid #16a34a;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 15px 0;
    }
    .disclaimer-badge {
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        color: #475569;
        font-size: 11px;
        padding: 4px 8px;
        border-radius: 4px;
        display: inline-block;
        font-weight: 500;
    }
    
    /* Pill status badges */
    .pill-red {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
    }
    .pill-amber {
        background-color: #fef3c7;
        color: #92400e;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
    }
    .pill-green {
        background-color: #dcfce7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 11px;
        font-weight: 700;
    }
    
    /* Code highlight */
    .formula-tag {
        font-family: monospace;
        background-color: #f1f5f9;
        padding: 2px 6px;
        border-radius: 4px;
        color: #0f172a;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. State & Data Initialization (Cached for performance & consistency)
# -----------------------------------------------------------------------------
@st.cache_data
def load_datasets():
    hist_df = generate_historical_orders(num_orders=250, seed=42)
    live_df = generate_live_orders(seed=101)
    return hist_df, live_df

historical_df, live_orders_df = load_datasets()
baseline_metrics = calculate_stage_metrics(historical_df)
metrics_df = baseline_metrics["metrics_df"]
slowest_stage_name = baseline_metrics["slowest_stage_name"]

# -----------------------------------------------------------------------------
# 3. Sidebar Controls & Global What-If Parameters
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚡ **FlowFix Navigation**")
    nav_selection = st.radio(
        "Choose App Section:",
        [
            "1. 📊 Bottleneck Detective",
            "2. ⏳ What-If Time Machine",
            "3. 🩺 Root Cause Detective",
            "4. 🚨 Order Delay Early Warning",
            "5. 💰 Business Impact Calculator",
            "6. 🎓 Expo Pitch & Methodology"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 🎛️ **What-If Simulation Controls**")
    st.caption("Adjust estimated stage improvements to see real-time recalculations.")
    
    # Sliders for stage reductions in minutes
    s1_red = st.slider("Order Received Reduction (mins):", min_value=0, max_value=8, value=4, step=1,
                       help="Automation of API webhook ingestion.")
    s2_red = st.slider("Payment Verification Reduction (mins):", min_value=0, max_value=15, value=10, step=1,
                       help="Instant validation for verified returning customers.")
    s3_red = st.slider("Picking & Packing Reduction (mins):", min_value=0, max_value=75, value=38, step=1,
                       help="Warehouse wave picking & SKU velocity zoning.")
    s4_red = st.slider("Dispatch Reduction (mins):", min_value=0, max_value=25, value=12, step=1,
                       help="Pre-sorted carrier bays & dual daily pickup.")
    
    reduction_dict = {
        "Order Received": float(s1_red),
        "Payment Verification": float(s2_red),
        "Picking and Packing": float(s3_red),
        "Dispatch": float(s4_red)
    }
    
    st.markdown("---")
    st.markdown("### 💼 **Volume & Cost Assumptions**")
    daily_orders = st.number_input("Daily Orders Processed:", min_value=10, max_value=50000, value=250, step=25)
    hourly_labor_rate = st.number_input("Hourly Warehouse Labor Cost ($/hr):", min_value=0.0, max_value=200.0, value=18.5, step=0.5)
    
    st.markdown("---")
    st.caption("🔒 **FlowFix College Expo Edition**\n- 100% Local Execution\n- No External API Keys Needed\n- Offline Demonstration Mode")

# -----------------------------------------------------------------------------
# 4. Global Simulation Calculations
# -----------------------------------------------------------------------------
sim_results = simulate_what_if(
    original_metrics_df=metrics_df,
    reduction_dict=reduction_dict,
    daily_orders=daily_orders,
    hourly_wage=hourly_labor_rate
)

baseline_score_data = calculate_efficiency_score(historical_df)
simulated_score_data = calculate_efficiency_score(historical_df, simulated_stage_times=sim_results["simulated_stage_times"])

# -----------------------------------------------------------------------------
# 5. Application Header & Top Summary Metric Cards
# -----------------------------------------------------------------------------
st.markdown("""
<div class="flowfix-header">
    <span class="flowfix-badge">College Project Expo 2026 • AI Workflow Intelligence</span>
    <h1 class="flowfix-title">⚡ FlowFix — AI Workflow Bottleneck Detective</h1>
    <div class="flowfix-tagline">"Find the bottleneck. Fix the flow." • End-to-end e-commerce fulfillment latency analyzer</div>
</div>
""", unsafe_allow_html=True)

# Prominent Sample Data Banner
st.markdown("""
<div style="background-color: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; padding: 8px 14px; border-radius: 6px; font-size: 13px; margin-bottom: 18px; display: flex; align-items: center; justify-content: space-between;">
    <span>📌 <b>DEMONSTRATION SAMPLE DATA:</b> All metrics, orders, and timestamps shown are generated synthetic benchmarks calibrated to representative e-commerce operations.</span>
    <span class="disclaimer-badge">REPRODUCIBLE BENCHMARK</span>
</div>
""", unsafe_allow_html=True)

# Top 4 KPI Metrics (Always Visible)
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Current Cycle Time</div>
        <div class="metric-value">{baseline_metrics['avg_total_mins']} <span style="font-size:16px;font-weight:500;">mins</span></div>
        <div class="metric-sub-neutral">~{baseline_metrics['avg_total_hours']} hours per order</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Primary Bottleneck</div>
        <div class="metric-value" style="color: #ea580c; font-size:22px;">{baseline_metrics['slowest_stage_name']}</div>
        <div class="metric-sub-alert">Consumes {baseline_metrics['slowest_stage_pct']}% of total time</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Simulated Savings</div>
        <div class="metric-value" style="color: #10b981;">-{sim_results['total_saved_mins_per_order']} <span style="font-size:16px;font-weight:500;">mins</span></div>
        <div class="metric-sub">▼ {sim_results['total_saved_pct']}% Cycle Time Reduction</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    score_delta = round(simulated_score_data['score'] - baseline_score_data['score'], 1)
    delta_str = f"+{score_delta}" if score_delta >= 0 else f"{score_delta}"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">FlowFix Efficiency Score</div>
        <div class="metric-value">{baseline_score_data['score']} <span style="font-size:16px;color:#2563eb;">➔ {simulated_score_data['score']}</span></div>
        <div class="metric-sub">▲ {delta_str} pts with simulated fixes</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SECTION 1: BOTTLENECK DETECTIVE
# -----------------------------------------------------------------------------
if nav_selection.startswith("1."):
    st.markdown("## 🔍 Bottleneck Detective: Stage-by-Stage Analysis")
    st.markdown(
        "FlowFix measures the operational lead time across all 4 stages of order fulfillment: "
        "**Order Received ➔ Payment Verification ➔ Picking and Packing ➔ Dispatch**."
    )
    
    # Bottleneck alert banner
    slowest_row = metrics_df[metrics_df["stage_name"] == slowest_stage_name].iloc[0]
    st.markdown(f"""
    <div class="bottleneck-box">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="font-size:18px; font-weight:800; color:#9a3412;">🚨 PRIMARY BOTTLENECK DETECTED: {slowest_stage_name.upper()}</span>
            <span class="disclaimer-badge">CRITICAL CONSTRAINED RESOURCE</span>
        </div>
        <p style="margin: 8px 0 4px 0; color:#7c2d12; font-size:14px; line-height: 1.5;">
            <b>Why is this a bottleneck?</b> Orders take an average of <b>{slowest_row['avg_mins']} minutes</b> in 
            <b>{slowest_stage_name}</b>, which accounts for <b>{slowest_row['pct_share']}%</b> of the entire order lifespan. 
            Because upstream payment orders arrive faster than warehouse staff can pick and pack items, an inventory queue builds up, 
            causing dispatch delays regardless of how quickly subsequent stages operate.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Charts row
    col_left, col_right = st.columns([7, 5])
    
    with col_left:
        fig_bar = create_stage_distribution_chart(metrics_df, slowest_stage_name)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_right:
        fig_donut = create_stage_share_donut(metrics_df, slowest_stage_name)
        st.plotly_chart(fig_donut, use_container_width=True)
        
    st.markdown("### 📋 Measured Stage Performance Table")
    
    # Clean display dataframe
    display_table = metrics_df[["stage_name", "avg_mins", "median_mins", "min_mins", "max_mins", "pct_share", "target_sla_mins"]].copy()
    display_table.columns = [
        "Workflow Stage", "Average (mins)", "Median (mins)", "Fastest (mins)", "Slowest (mins)", "% of Total Cycle", "Stage Target (mins)"
    ]
    
    st.dataframe(
        display_table.style.highlight_max(subset=["Average (mins)"], color="#fee2e2"),
        use_container_width=True,
        hide_index=True
    )
    
    # Practical Recommendation Callout
    rec = get_recommendation_for_stage(slowest_stage_name)
    st.markdown(f"""
    <div class="success-box">
        <div style="font-size:16px; font-weight:700; color:#166534;">💡 FlowFix Recommendation for {slowest_stage_name}: {rec['recommendation']['title']}</div>
        <p style="margin: 6px 0; color:#14532d; font-size:13.5px; white-space: pre-line;">
            {rec['recommendation']['action']}
        </p>
        <div style="display:flex; justify-content:space-between; margin-top:8px; font-size:12px; color:#166534; font-weight:600;">
            <span>Expected Impact: {rec['recommendation']['expected_benefit']}</span>
            <span>Effort: {rec['recommendation']['effort']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SECTION 2: INTERACTIVE WHAT-IF TIME MACHINE
# -----------------------------------------------------------------------------
elif nav_selection.startswith("2."):
    st.markdown("## ⏳ Interactive What-If Time Machine")
    st.markdown(
        "Simulate operational interventions to see how shaving minutes off individual stages collapses "
        "the total order fulfillment cycle. All recalculations are instantaneous."
    )
    
    st.markdown("""
    <div style="background-color: #f1f5f9; padding: 10px 16px; border-radius: 8px; font-size: 13px; color: #334155; margin-bottom: 16px;">
        ⚙️ <b>Active Simulation Parameters:</b> Use the sliders on the left sidebar to change stage improvements.
        Current inputs: <b>Order Received (-{s1_red}m)</b>, <b>Payment (-{s2_red}m)</b>, <b>Picking & Packing (-{s3_red}m)</b>, <b>Dispatch (-{s4_red}m)</b>.
    </div>
    """.format(s1_red=s1_red, s2_red=s2_red, s3_red=s3_red, s4_red=s4_red), unsafe_allow_html=True)
    
    # Before & After Chart
    fig_comp = create_before_after_chart(
        sim_results["sim_df"],
        sim_results["total_original_mins"],
        sim_results["total_simulated_mins"]
    )
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # Comparison Summary Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Baseline Total Cycle", f"{sim_results['total_original_mins']} mins", help="Historical average")
    with c2:
        st.metric("Simulated Total Cycle", f"{sim_results['total_simulated_mins']} mins", f"-{sim_results['total_saved_mins_per_order']} mins", delta_color="inverse")
    with c3:
        st.metric("Cycle Time Reduction", f"{sim_results['total_saved_pct']}%", "Speed Gain")
    with c4:
        st.metric("Time Saved / 100 Orders", f"{round(sim_results['total_saved_mins_per_order'] * 100 / 60, 1)} hrs", "Labor Equivalent")
        
    st.markdown("### 📊 Stage-by-Stage Simulation Breakdown")
    sim_table = sim_results["sim_df"].copy()
    sim_table.columns = ["Workflow Stage", "Baseline (mins)", "Simulated (mins)", "Time Saved (mins)", "% Reduction"]
    st.dataframe(sim_table, use_container_width=True, hide_index=True)
    
    st.markdown("""
    <div class="callout-box">
        <b>Simulation Assumption Note:</b> All simulated reductions represent realistic target goals assuming operational changes 
        (such as batch picking or automated webhooks) are successfully implemented. Processing times are constrained to a realistic minimum physical threshold.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SECTION 3: ROOT CAUSE DETECTIVE
# -----------------------------------------------------------------------------
elif nav_selection.startswith("3."):
    st.markdown("## 🩺 Root Cause Detective")
    st.markdown(
        "Diagnose *why* bottlenecks occur. FlowFix clearly separates **Confirmed Findings** (proven by order timestamp data) "
        "from **Unverified Hypotheses** (potential physical warehouse or software causes that require on-site verification)."
    )
    
    catalog = get_root_cause_catalog()
    stage_choices = [item["stage"] for item in catalog]
    
    selected_stage_name = st.selectbox(
        "Select Workflow Stage to Investigate:",
        stage_choices,
        index=0
    )
    
    selected_issue = next(item for item in catalog if item["stage"] == selected_stage_name)
    
    # Severity Badge
    st.markdown(f"""
    <div style="margin: 12px 0 16px 0;">
        <span class="pill-red" style="font-size:13px;">STATUS: {selected_issue['severity']}</span>
        <span style="font-size: 19px; font-weight: 700; margin-left: 10px; color:#0f172a;">{selected_issue['title']}</span>
    </div>
    """, unsafe_allow_html=True)
    
    col_diag_left, col_diag_right = st.columns(2)
    
    with col_diag_left:
        st.markdown("#### ✅ Confirmed Finding from Sample Data")
        st.info(selected_issue["confirmed_finding"])
        
        st.markdown("#### 🔍 Unverified Operational Hypotheses")
        st.markdown("*These are educated hypotheses based on standard warehouse operations; they require physical verification:*")
        for hypo in selected_issue["unverified_hypotheses"]:
            st.markdown(f"- ❓ {hypo}")
            
    with col_diag_right:
        st.markdown("#### 📋 On-Site Diagnostic Checklist")
        st.markdown("*Steps for warehouse and operations leads to confirm hypotheses:*")
        for step in selected_issue["diagnostic_checklist"]:
            st.markdown(f"- [ ] {step}")
            
        st.markdown("#### 🚀 Actionable Solution")
        rec_info = selected_issue["recommendation"]
        st.markdown(f"""
        <div class="success-box" style="margin-top: 10px;">
            <b>{rec_info['title']}</b>
            <p style="margin: 6px 0; font-size:13px; white-space:pre-line;">{rec_info['action']}</p>
            <div style="font-size:12px; margin-top:6px; color:#166534;">
                <b>Expected Impact:</b> {rec_info['expected_benefit']}<br>
                <b>Implementation Effort:</b> {rec_info['effort']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SECTION 4: ORDER DELAY EARLY WARNING
# -----------------------------------------------------------------------------
elif nav_selection.startswith("4."):
    st.markdown("## 🚨 Order Delay Early Warning Radar")
    st.markdown(
        "Real-time monitoring for active orders currently progressing through the fulfillment pipeline. "
        "Orders are evaluated against SLA cut-off deadlines using transparent, explainable operational rules."
    )
    
    # Quick Status Summary Bar
    status_counts = live_orders_df["status"].value_counts()
    c_overdue = status_counts.get("CRITICAL: Overdue", 0)
    c_risk = status_counts.get("WARNING: At Risk", 0)
    c_healthy = status_counts.get("HEALTHY: On Track", 0)
    
    w1, w2, w3, w4 = st.columns(4)
    with w1:
        st.metric("Total Active Orders", len(live_orders_df))
    with w2:
        st.metric("Critical Overdue Orders", c_overdue, "SLA Breached", delta_color="inverse")
    with w3:
        st.metric("At-Risk Orders", c_risk, "High Urgency", delta_color="inverse")
    with w4:
        st.metric("Healthy / On-Track", c_healthy, "Within Window")
        
    # Interactive Radar Scatter
    fig_radar = create_live_radar_scatter(live_orders_df)
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # Filter controls
    st.markdown("### 🔎 Active Orders Inspection Table")
    f_col1, f_col2 = st.columns([3, 3])
    with f_col1:
        status_filter = st.multiselect(
            "Filter by Warning Status:",
            ["CRITICAL: Overdue", "WARNING: At Risk", "HEALTHY: On Track"],
            default=["CRITICAL: Overdue", "WARNING: At Risk", "HEALTHY: On Track"]
        )
    with f_col2:
        stage_filter = st.multiselect(
            "Filter by Current Stage:",
            ["Order Received", "Payment Verification", "Picking and Packing", "Dispatch"],
            default=["Order Received", "Payment Verification", "Picking and Packing", "Dispatch"]
        )
        
    filtered_orders = live_orders_df[
        (live_orders_df["status"].isin(status_filter)) &
        (live_orders_df["current_stage"].isin(stage_filter))
    ]
    
    # Display table
    show_table = filtered_orders[[
        "order_id", "customer_name", "priority", "current_stage", "elapsed_mins", "deadline_mins", "sla_consumed_pct", "status", "warning_reason"
    ]].copy()
    show_table.columns = [
        "Order ID", "Customer", "Priority", "Current Stage", "Elapsed (m)", "SLA (m)", "SLA Used %", "Status", "Reason / Diagnostic"
    ]
    
    st.dataframe(show_table, use_container_width=True, hide_index=True)
    
    st.markdown("""
    <div class="callout-box">
        <b>Explainable Early Warning Rules:</b>
        <ul>
            <li><b>CRITICAL: Overdue</b> ➔ Elapsed processing time has already strictly exceeded the guaranteed dispatch deadline (<span class="formula-tag">Elapsed &gt; SLA</span>).</li>
            <li><b>WARNING: At Risk</b> ➔ Order has consumed &ge; 75% of its SLA deadline but is still stuck in an upstream stage (<span class="formula-tag">Elapsed &ge; 0.75 * SLA and Stage &ne; Dispatch</span>).</li>
            <li><b>HEALTHY: On Track</b> ➔ Order is progressing within normal velocity parameters.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SECTION 5: BUSINESS IMPACT CALCULATOR
# -----------------------------------------------------------------------------
elif nav_selection.startswith("5."):
    st.markdown("## 💰 Business Impact Calculator")
    st.markdown(
        "Quantify the compounding operational and financial return of removing workflow bottlenecks. "
        "Small minutes saved per order scale into thousands of labor hours saved across commercial order volumes."
    )
    
    # Volume metrics
    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Daily Labor Time Saved</div>
            <div class="metric-value">{sim_results['daily_hours_saved']} <span style="font-size:16px;">hrs/day</span></div>
            <div class="metric-sub">Based on {daily_orders} daily orders</div>
        </div>
        """, unsafe_allow_html=True)
        
    with b2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Monthly Labor Time Saved</div>
            <div class="metric-value">{sim_results['monthly_hours_saved']} <span style="font-size:16px;">hrs/mo</span></div>
            <div class="metric-sub">~{round(sim_results['monthly_hours_saved'] / 8, 1)} full work shifts</div>
        </div>
        """, unsafe_allow_html=True)
        
    with b3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Annual Labor Potential</div>
            <div class="metric-value">{sim_results['annual_hours_saved']:,} <span style="font-size:16px;">hrs/yr</span></div>
            <div class="metric-sub">Capacity unlocked for growth</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    
    # Financial projection section
    st.markdown("### 💵 Estimated Labor Value Unlock")
    if hourly_labor_rate > 0:
        f1, f2, f3 = st.columns(3)
        with f1:
            st.metric("Daily Potential Value", f"${sim_results['daily_cost_saved']:,.2f}")
        with f2:
            st.metric("Monthly Potential Value", f"${sim_results['monthly_cost_saved']:,.2f}")
        with f3:
            st.metric("Annual Potential Value", f"${sim_results['annual_cost_saved']:,.2f}")
    else:
        st.info("Enter an hourly labor rate in the sidebar to view monetary value estimates.")
        
    # Transparent formulas callout
    st.markdown("""
    <div class="callout-box">
        <h4 style="margin:0 0 8px 0; color:#1e293b;">📐 Transparent Calculation Formulas</h4>
        <ul>
            <li><b>Time Saved Per Order:</b> <span class="formula-tag">Total Saved (mins) = Baseline Avg (mins) - Simulated Avg (mins)</span></li>
            <li><b>Daily Hours Saved:</b> <span class="formula-tag">Daily Hours = (Time Saved Per Order × Daily Orders) ÷ 60</span></li>
            <li><b>Annual Labor Value:</b> <span class="formula-tag">Annual Value ($) = Daily Hours × 365 × Hourly Labor Rate</span></li>
        </ul>
        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 10px 0;">
        <span style="font-size:12px; color:#64748b;">
            ⚠️ <b>Honest Business Disclaimer:</b> Processing-time savings do not automatically reduce payroll expenses 
            unless staff hours are physically reduced or overtime is eliminated. In real-world warehouses, time savings are 
            primarily captured by <b>increasing maximum order capacity without hiring additional staff</b> and 
            <b>avoiding SLA breach penalties</b>.
        </span>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SECTION 6: EXPO PITCH & METHODOLOGY
# -----------------------------------------------------------------------------
elif nav_selection.startswith("6."):
    st.markdown("## 🎓 College Expo Presentation & Methodology Guide")
    st.markdown(
        "Use this section to prepare your presentation to college project expo judges. "
        "It includes a 3-minute pitch script, formula transparency, and honest technical limitations."
    )
    
    tab_pitch, tab_formula, tab_limits = st.tabs([
        "🎤 3-Minute Judge Pitch Script",
        "📐 FlowFix Score Formula",
        "⚖️ Honest Limitations & Future Scope"
    ])
    
    with tab_pitch:
        st.markdown("""
        ### 🎙️ The 3-Minute Expo Elevator Pitch
        
        **1. The Hook (0:00 - 0:45):**
        > *"Judges, in modern e-commerce, customer expectations are defined by same-day delivery. But most fulfillment centers have no idea where orders are actually getting stuck between click and dispatch. They guess that shipping is slow, but the real culprit is usually an invisible warehouse bottleneck. That's why we built **FlowFix — AI Workflow Bottleneck Detective**."*
        
        **2. The Live Demo (0:45 - 2:00):**
        > *"Our app analyzes order milestones across 4 stages. As you can see on the Bottleneck Detective screen, **Picking & Packing** alone consumes 142 minutes—that's over 65% of the entire cycle!*
        >
        > *Next, we toggle our **Interactive What-If Time Machine**. By implementing wave picking, we simulate cutting 38 minutes from picking. FlowFix instantly recalculates our total cycle time, showing a 22% drop and saving over 150 hours every single day for an operation with 250 orders.*
        >
        > *Finally, our **Root Cause Detective** separates data facts from hypotheses, while our **Early Warning Radar** flags orders approaching their SLA deadline before they become late."*
        
        **3. The Conclusion (2:00 - 3:00):**
        > *"FlowFix transforms raw order timestamps into actionable warehouse intelligence without expensive ERP software or complex databases. Thank you, and we'd love to take your questions!"*
        """)
        
    with tab_formula:
        st.markdown(r"""
        ### 📐 FlowFix Efficiency Score Methodology
        
        Rather than generating arbitrary 'AI' scores, FlowFix uses an explainable, deterministic mathematical model:
        
        $$\text{Score} = (0.40 \times \text{SLA Compliance}) + (0.35 \times \text{Balance Index}) + (0.25 \times \text{Velocity Index})$$
        
        | Component | Weight | Logic & Formula |
        |---|---|---|
        | **SLA Compliance** | 40% | Percentage of orders that meet their promised delivery cutoff window ($\le 180\text{m}$ or $240\text{m}$). |
        | **Workflow Balance** | 35% | Evaluates whether work flows smoothly or piles up in one station: $100 - (\text{Max Stage Share}\% - 25\%) \times 1.8$. Perfect balance is 25% per stage. |
        | **Velocity Index** | 25% | Compares average speed against an industry standard 150-minute benchmark: $(150 / \text{Total Avg Mins}) \times 100$. |
        """)
        
        # Live Efficiency Gauge
        st.markdown("#### Live Efficiency Score Gauge")
        fig_gauge = create_efficiency_gauge(baseline_score_data["score"], simulated_score_data["score"])
        st.plotly_chart(fig_gauge, use_container_width=True)
        
    with tab_limits:
        st.markdown("""
        ### ⚖️ Honest Limitations to Acknowledge to Judges
        
        A great project defense openly acknowledges constraints:
        
        1. **Timestamp Granularity:**
           * *Current:* FlowFix calculates stage durations from milestone timestamps (order placed, payment verified, pick started/finished, manifested).
           * *Limitation:* It does not track internal sub-steps (e.g. picker walking vs searching vs scanning) without IoT warehouse beacons or RFID.
           
        2. **Synthetic Demonstration Data:**
           * *Current:* Uses statistically calibrated synthetic order data for reliable demonstration.
           * *Next Step:* Connecting via REST API or CSV file upload to real Shopify / WooCommerce / ShipStation webhooks.
           
        3. **Deterministic vs Black-Box AI:**
           * *Design Choice:* We intentionally used explainable statistical rules and queue theory rather than opaque deep neural networks so warehouse managers can understand and trust every recommendation.
        """)

# -----------------------------------------------------------------------------
# 6. Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 12px; margin-bottom: 20px;">
    ⚡ <b>FlowFix — AI Workflow Bottleneck Detective</b> • Built with Python, Streamlit, Pandas & Plotly • College Project Expo
</div>
""", unsafe_allow_html=True)
