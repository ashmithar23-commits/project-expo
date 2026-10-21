"""
analyzer.py - Workflow analytics engine for FlowFix.

Contains pure calculation functions:
- Stage duration calculations
- Bottleneck identification
- FlowFix Efficiency Score formula & breakdown
- What-If simulation mathematics
- Business impact estimates
"""

import pandas as pd
import numpy as np
from data_generator import get_stage_definitions

def calculate_stage_metrics(df):
    """
    Computes statistical metrics for each of the 4 workflow stages.
    Identifies the slowest stage and its percentage share.
    """
    stages = get_stage_definitions()
    results = []
    
    total_avg_time = 0.0
    for s in stages:
        col = s["column"]
        avg_val = float(df[col].mean())
        total_avg_time += avg_val
        
    for s in stages:
        col = s["column"]
        series = df[col]
        avg_val = float(series.mean())
        median_val = float(series.median())
        min_val = float(series.min())
        max_val = float(series.max())
        pct_share = round((avg_val / total_avg_time) * 100, 1) if total_avg_time > 0 else 0.0
        
        results.append({
            "stage_id": s["id"],
            "stage_name": s["name"],
            "column": col,
            "description": s["description"],
            "target_sla_mins": s["target_sla_mins"],
            "avg_mins": round(avg_val, 1),
            "median_mins": round(median_val, 1),
            "min_mins": round(min_val, 1),
            "max_mins": round(max_val, 1),
            "pct_share": pct_share
        })
        
    metrics_df = pd.DataFrame(results)
    
    # Identify slowest stage
    slowest_row = metrics_df.loc[metrics_df["avg_mins"].idxmax()]
    
    # Calculate overall order stats
    avg_total_mins = round(float(df["total_duration_mins"].mean()), 1)
    median_total_mins = round(float(df["total_duration_mins"].median()), 1)
    sla_compliance_rate = round(float(df["sla_met"].mean() * 100), 1)
    
    summary = {
        "metrics_df": metrics_df,
        "avg_total_mins": avg_total_mins,
        "avg_total_hours": round(avg_total_mins / 60.0, 2),
        "median_total_mins": median_total_mins,
        "sla_compliance_rate": sla_compliance_rate,
        "slowest_stage_name": slowest_row["stage_name"],
        "slowest_stage_avg": slowest_row["avg_mins"],
        "slowest_stage_pct": slowest_row["pct_share"],
        "slowest_stage_id": slowest_row["stage_id"]
    }
    
    return summary

def calculate_efficiency_score(df, simulated_stage_times=None):
    """
    Computes the transparent FlowFix Efficiency Score (0-100).
    
    FORMULA ARCHITECTURE:
    ---------------------
    Score = (0.40 * SLA_Compliance_Score) + (0.35 * Balance_Score) + (0.25 * Velocity_Score)
    
    1. SLA Compliance Score (40% weight):
       Percentage of orders completed within their guaranteed SLA window.
       
    2. Workflow Balance Score (35% weight):
       Measures how evenly load is distributed across the 4 stages.
       In an ideal pipeline, stages are balanced (~25% each).
       Formula: max(10, 100 - (max_stage_share_pct - 25.0) * 1.8)
       If one stage hoggs 65% of the time, Balance Score drops significantly.
       
    3. Velocity Score (25% weight):
       Measures average cycle speed against an industry benchmark (150 minutes).
       Formula: min(100, max(20, (150.0 / total_avg_mins) * 100))
    """
    stages = get_stage_definitions()
    
    if simulated_stage_times is None:
        # Baseline calculations
        avg_total = float(df["total_duration_mins"].mean())
        sla_comp = float(df["sla_met"].mean() * 100)
        
        # Max stage share
        stage_avgs = [float(df[s["column"]].mean()) for s in stages]
        max_share = (max(stage_avgs) / sum(stage_avgs)) * 100.0 if sum(stage_avgs) > 0 else 25.0
        
    else:
        # Simulated calculations
        stage_avgs = [simulated_stage_times[s["name"]] for s in stages]
        avg_total = sum(stage_avgs)
        max_share = (max(stage_avgs) / avg_total) * 100.0 if avg_total > 0 else 25.0
        
        # Estimate simulated SLA compliance by shifting historical distribution
        orig_avg = float(df["total_duration_mins"].mean())
        delta = orig_avg - avg_total
        # Simulated duration for each order
        sim_durations = np.maximum(20.0, df["total_duration_mins"] - delta)
        sim_sla_met = sim_durations <= df["target_sla_mins"]
        sla_comp = float(sim_sla_met.mean() * 100)
        
    # Component 1: SLA Compliance (0-100)
    c1_sla = round(np.clip(sla_comp, 0.0, 100.0), 1)
    
    # Component 2: Flow Balance (0-100)
    # 25% is perfect equal balance. If a bottleneck takes 65%, delta is 40 -> 100 - 40*1.8 = 28
    c2_balance = round(float(np.clip(100.0 - (max_share - 25.0) * 1.8, 15.0, 100.0)), 1)
    
    # Component 3: Velocity (0-100)
    benchmark_mins = 150.0
    c3_velocity = round(float(np.clip((benchmark_mins / max(1.0, avg_total)) * 100.0, 20.0, 100.0)), 1)
    
    # Weighted composite
    composite = round(0.40 * c1_sla + 0.35 * c2_balance + 0.25 * c3_velocity, 1)
    
    return {
        "score": composite,
        "sla_score": c1_sla,
        "balance_score": c2_balance,
        "velocity_score": c3_velocity,
        "avg_total_mins": round(avg_total, 1),
        "max_stage_share": round(max_share, 1)
    }

def simulate_what_if(original_metrics_df, reduction_dict, daily_orders=200, hourly_wage=20.0):
    """
    Recalculates workflow duration and business impacts given user reduction inputs.
    
    reduction_dict: { "Stage Name": minutes_saved_or_percent }
    """
    sim_data = []
    total_orig = 0.0
    total_sim = 0.0
    
    for _, row in original_metrics_df.iterrows():
        s_name = row["stage_name"]
        orig_mins = row["avg_mins"]
        reduced_mins = float(reduction_dict.get(s_name, 0.0))
        
        new_mins = round(max(2.0, orig_mins - reduced_mins), 1)
        mins_saved = round(orig_mins - new_mins, 1)
        pct_saved = round((mins_saved / orig_mins) * 100, 1) if orig_mins > 0 else 0.0
        
        total_orig += orig_mins
        total_sim += new_mins
        
        sim_data.append({
            "stage_name": s_name,
            "original_mins": orig_mins,
            "simulated_mins": new_mins,
            "mins_saved": mins_saved,
            "pct_saved": pct_saved
        })
        
    sim_df = pd.DataFrame(sim_data)
    
    total_orig = round(total_orig, 1)
    total_sim = round(total_sim, 1)
    total_saved_mins = round(total_orig - total_sim, 1)
    total_saved_pct = round((total_saved_mins / total_orig) * 100, 1) if total_orig > 0 else 0.0
    
    # Volume projections
    daily_mins_saved = round(total_saved_mins * daily_orders, 1)
    daily_hours_saved = round(daily_mins_saved / 60.0, 1)
    
    monthly_orders = daily_orders * 30
    monthly_hours_saved = round(daily_hours_saved * 30, 1)
    
    annual_orders = daily_orders * 365
    annual_hours_saved = round(daily_hours_saved * 365, 1)
    
    # Financial estimate (hypothetical)
    daily_cost_saved = round(daily_hours_saved * hourly_wage, 2)
    monthly_cost_saved = round(monthly_hours_saved * hourly_wage, 2)
    annual_cost_saved = round(annual_hours_saved * hourly_wage, 2)
    
    simulated_stage_times = {row["stage_name"]: row["simulated_mins"] for _, row in sim_df.iterrows()}
    
    return {
        "sim_df": sim_df,
        "total_original_mins": total_orig,
        "total_simulated_mins": total_sim,
        "total_saved_mins_per_order": total_saved_mins,
        "total_saved_hours_per_order": round(total_saved_mins / 60.0, 2),
        "total_saved_pct": total_saved_pct,
        "daily_orders": daily_orders,
        "daily_hours_saved": daily_hours_saved,
        "monthly_orders": monthly_orders,
        "monthly_hours_saved": monthly_hours_saved,
        "annual_orders": annual_orders,
        "annual_hours_saved": annual_hours_saved,
        "hourly_wage": hourly_wage,
        "daily_cost_saved": daily_cost_saved,
        "monthly_cost_saved": monthly_cost_saved,
        "annual_cost_saved": annual_cost_saved,
        "simulated_stage_times": simulated_stage_times
    }
