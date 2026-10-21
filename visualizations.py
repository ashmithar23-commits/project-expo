"""
visualizations.py - Interactive Plotly charts for FlowFix.

Contains chart builders:
- Stage duration & percentage share horizontal bar chart
- Stage percentage share donut chart
- Before-and-After What-If comparison grouped bar chart
- FlowFix Efficiency Score dual-indicator gauge
- Live order status radar scatter/timeline
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Professional color palette for college expo presentation
COLOR_PRIMARY = "#2563eb"     # Royal Blue
COLOR_ACCENT = "#f97316"      # Orange/Coral (Bottleneck)
COLOR_SUCCESS = "#10b981"     # Emerald Green
COLOR_WARNING = "#f59e0b"     # Amber
COLOR_DANGER = "#ef4444"      # Crimson Red
COLOR_MUTED = "#64748b"       # Slate
COLOR_BG_CARD = "#ffffff"     # White card bg

def create_stage_distribution_chart(metrics_df, slowest_stage_name):
    """
    Horizontal bar chart displaying average duration for each workflow stage.
    Highlights the slowest stage in vivid coral.
    """
    # Sort order to display in natural workflow sequence (reverse for horizontal bar)
    df_plot = metrics_df.copy()
    
    colors = [
        COLOR_ACCENT if row["stage_name"] == slowest_stage_name else "#3b82f6"
        for _, row in df_plot.iterrows()
    ]
    
    labels = [
        f"<b>{row['avg_mins']} mins</b> ({row['pct_share']}%)" + (" 🚨 BOTTLENECK" if row["stage_name"] == slowest_stage_name else "")
        for _, row in df_plot.iterrows()
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_plot["stage_name"],
        x=df_plot["avg_mins"],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color="#1e293b", width=1)
        ),
        text=labels,
        textposition='outside',
        textfont=dict(size=12, color="#0f172a"),
        hovertemplate="<b>Stage:</b> %{y}<br>" +
                      "<b>Avg Time:</b> %{x:.1f} minutes<br>" +
                      "<b>Share of Total:</b> %{customdata[0]}%<br>" +
                      "<b>Min - Max:</b> %{customdata[1]}m - %{customdata[2]}m<extra></extra>",
        customdata=df_plot[["pct_share", "min_mins", "max_mins"]]
    ))
    
    max_x = df_plot["avg_mins"].max() * 1.35
    
    fig.update_layout(
        title=dict(
            text="<b>Average Duration by Workflow Stage</b> (Sample Data)",
            font=dict(size=15, color="#1e293b")
        ),
        xaxis=dict(
            title="Average Duration (Minutes)",
            range=[0, max_x],
            gridcolor="#e2e8f0",
            showgrid=True
        ),
        yaxis=dict(
            title="",
            autorange="reversed",
            tickfont=dict(size=13, color="#1e293b")
        ),
        plot_bgcolor="#f8fafc",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=45, b=30),
        height=300
    )
    
    return fig

def create_stage_share_donut(metrics_df, slowest_stage_name):
    """
    Donut chart illustrating percentage share of total order cycle time.
    """
    colors = [
        COLOR_ACCENT if s == slowest_stage_name else c
        for s, c in zip(metrics_df["stage_name"], ["#60a5fa", "#3b82f6", "#1d4ed8", "#93c5fd"])
    ]
    
    fig = go.Figure(data=[go.Pie(
        labels=metrics_df["stage_name"],
        values=metrics_df["avg_mins"],
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
        textinfo="label+percent",
        textfont=dict(size=11),
        hovertemplate="<b>%{label}</b><br>Avg: %{value:.1f} mins (%{percent})<extra></extra>"
    )])
    
    fig.update_layout(
        title=dict(
            text="<b>Cycle Time Share (%)</b>",
            font=dict(size=15, color="#1e293b")
        ),
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=10, r=10, t=40, b=10),
        height=300,
        annotations=[dict(text="<b>FlowFix</b><br>Share", x=0.5, y=0.5, font_size=13, showarrow=False)]
    )
    
    return fig

def create_before_after_chart(sim_df, total_orig, total_sim):
    """
    Grouped bar chart comparing Original vs Simulated processing times across stages + Total.
    """
    stages = list(sim_df["stage_name"]) + ["TOTAL CYCLE"]
    orig_vals = list(sim_df["original_mins"]) + [total_orig]
    sim_vals = list(sim_df["simulated_mins"]) + [total_sim]
    savings = list(sim_df["mins_saved"]) + [round(total_orig - total_sim, 1)]
    
    fig = go.Figure()
    
    # Original Bar
    fig.add_trace(go.Bar(
        name="Original (Baseline)",
        x=stages,
        y=orig_vals,
        marker_color="#94a3b8",
        text=[f"{v}m" for v in orig_vals],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Baseline: %{y} mins<extra></extra>"
    ))
    
    # Simulated Bar
    fig.add_trace(go.Bar(
        name="Simulated (FlowFix)",
        x=stages,
        y=sim_vals,
        marker_color="#10b981",
        text=[f"{v}m<br>(-{s}m)" if s > 0 else f"{v}m" for v, s in zip(sim_vals, savings)],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Simulated: %{y} mins<br>Saved: %{customdata} mins<extra></extra>",
        customdata=savings
    ))
    
    max_val = max(orig_vals) * 1.25
    
    fig.update_layout(
        title=dict(
            text="<b>Before vs. After Workflow Simulation</b> (Minutes per Order)",
            font=dict(size=15, color="#1e293b")
        ),
        barmode='group',
        xaxis=dict(title="", tickfont=dict(size=12, color="#1e293b")),
        yaxis=dict(
            title="Minutes",
            range=[0, max_val],
            gridcolor="#e2e8f0",
            showgrid=True
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor="#f8fafc",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=55, b=25),
        height=360
    )
    
    return fig

def create_efficiency_gauge(baseline_score, sim_score):
    """
    Dual indicator gauge comparing baseline efficiency score to simulated score.
    """
    delta = round(sim_score - baseline_score, 1)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=sim_score,
        delta={'reference': baseline_score, 'increasing': {'color': COLOR_SUCCESS}, 'suffix': " pts"},
        title={'text': "<b>FlowFix Efficiency Score (0 - 100)</b><br><span style='font-size:0.8em;color:gray'>Baseline: " + str(baseline_score) + " pts</span>", 'font': {'size': 14}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
            'bar': {'color': "#2563eb", 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 1,
            'bordercolor': "#cbd5e1",
            'steps': [
                {'range': [0, 50], 'color': '#fee2e2'},     # Critical Red
                {'range': [50, 75], 'color': '#fef3c7'},    # Warning Amber
                {'range': [75, 90], 'color': '#e0f2fe'},    # Good Blue
                {'range': [90, 100], 'color': '#dcfce7'}    # Optimal Green
            ],
            'threshold': {
                'line': {'color': "#dc2626", 'width': 3},
                'thickness': 0.85,
                'value': baseline_score
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=25, r=25, t=50, b=20),
        height=260
    )
    
    return fig

def create_live_radar_scatter(live_df):
    """
    Scatter visualization showing active orders across workflow stages vs their SLA deadlines.
    """
    status_color_map = {
        "CRITICAL: Overdue": COLOR_DANGER,
        "WARNING: At Risk": COLOR_WARNING,
        "HEALTHY: On Track": COLOR_SUCCESS
    }
    
    fig = px.scatter(
        live_df,
        x="elapsed_mins",
        y="current_stage",
        color="status",
        color_discrete_map=status_color_map,
        size="item_count",
        hover_name="order_id",
        hover_data={
            "customer_name": True,
            "deadline_mins": True,
            "sla_consumed_pct": ":.1f",
            "warning_reason": True,
            "current_stage": False,
            "elapsed_mins": False
        },
        category_orders={
            "current_stage": ["Order Received", "Payment Verification", "Picking and Packing", "Dispatch"]
        }
    )
    
    # Add SLA threshold vertical line
    fig.add_vline(x=180, line_width=1.5, line_dash="dash", line_color="#ef4444",
                  annotation_text="Express SLA (180m)", annotation_position="top left",
                  annotation_font_size=10, annotation_font_color="#ef4444")
    fig.add_vline(x=240, line_width=1.5, line_dash="dash", line_color="#b91c1c",
                  annotation_text="Standard SLA (240m)", annotation_position="top right",
                  annotation_font_size=10, annotation_font_color="#b91c1c")
    
    fig.update_layout(
        title=dict(
            text="<b>Live Order Delay Radar</b> (Active Orders by Stage & Elapsed Time)",
            font=dict(size=14, color="#1e293b")
        ),
        xaxis=dict(
            title="Elapsed Processing Time (Minutes)",
            gridcolor="#e2e8f0",
            showgrid=True
        ),
        yaxis=dict(
            title="",
            gridcolor="#f1f5f9"
        ),
        legend=dict(
            title=dict(text="Status"),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor="#f8fafc",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=50, b=30),
        height=340
    )
    
    return fig
