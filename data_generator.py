"""
data_generator.py - Synthetic e-commerce order workflow data generator for FlowFix.

Generates realistic, reproducible sample data for:
1. Historical completed orders (used for bottleneck analysis & efficiency scoring)
2. Live active orders (used for the Order Delay Early Warning system)

All data is synthetic sample data created for demonstration purposes.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_stage_definitions():
    """Returns canonical names and descriptions for the 4 workflow stages."""
    return [
        {
            "id": "stage_1",
            "name": "Order Received",
            "column": "order_received_mins",
            "description": "Order placement, payment gateway handoff, and inventory lock in the online store.",
            "target_sla_mins": 15
        },
        {
            "id": "stage_2",
            "name": "Payment Verification",
            "column": "payment_verification_mins",
            "description": "Fraud check, payment gateway settlement, and automated invoice generation.",
            "target_sla_mins": 25
        },
        {
            "id": "stage_3",
            "name": "Picking and Packing",
            "column": "picking_packing_mins",
            "description": "Physical warehouse item retrieval, barcode scan, packaging, and shipping label print.",
            "target_sla_mins": 90
        },
        {
            "id": "stage_4",
            "name": "Dispatch",
            "column": "dispatch_mins",
            "description": "Staging at loading dock, carrier handoff, manifest scanning, and vehicle departure.",
            "target_sla_mins": 35
        }
    ]

def generate_historical_orders(num_orders=250, seed=42):
    """
    Generates realistic historical order workflow records.
    Picking and Packing is realistically calibrated as the dominant bottleneck.
    """
    np.random.seed(seed)
    
    order_ids = [f"ORD-{1000 + i}" for i in range(num_orders)]
    customer_types = np.random.choice(["Standard", "Express", "Prime"], size=num_orders, p=[0.55, 0.30, 0.15])
    item_counts = np.random.choice([1, 2, 3, 4, 5, 7, 10], size=num_orders, p=[0.35, 0.25, 0.18, 0.10, 0.06, 0.04, 0.02])
    
    # Stage 1: Order Received (avg ~12 mins, low variance)
    s1 = np.random.normal(loc=12.5, scale=3.2, size=num_orders)
    s1 = np.clip(s1, 5.0, 30.0).round(1)
    
    # Stage 2: Payment Verification (avg ~24 mins; occasional fraud check spikes)
    s2_base = np.random.normal(loc=22.0, scale=6.0, size=num_orders)
    # 8% of orders trigger a manual fraud verification review
    s2_fraud_spike = np.random.choice([0, 35], size=num_orders, p=[0.92, 0.08])
    s2 = np.clip(s2_base + s2_fraud_spike, 8.0, 75.0).round(1)
    
    # Stage 3: Picking & Packing (THE PRIMARY BOTTLENECK: avg ~142 mins; scales with item count)
    s3_base = np.random.normal(loc=115.0, scale=28.0, size=num_orders)
    s3_item_factor = (item_counts - 1) * 11.5
    s3 = np.clip(s3_base + s3_item_factor, 55.0, 260.0).round(1)
    
    # Stage 4: Dispatch (avg ~38 mins; depends on daily carrier pickup cycles)
    s4 = np.random.normal(loc=38.0, scale=11.0, size=num_orders)
    s4 = np.clip(s4, 15.0, 85.0).round(1)
    
    total_duration = (s1 + s2 + s3 + s4).round(1)
    
    # SLA Targets: Standard = 240 mins (4 hrs), Express/Prime = 180 mins (3 hrs)
    target_sla = np.where(customer_types == "Standard", 240.0, 180.0)
    sla_met = total_duration <= target_sla
    
    # Generate realistic timestamps across the last 14 days
    base_date = datetime.now() - timedelta(days=14)
    timestamps = [base_date + timedelta(minutes=float(i * 75 + np.random.randint(-15, 15))) for i in range(num_orders)]
    
    df = pd.DataFrame({
        "order_id": order_ids,
        "created_at": [ts.strftime("%Y-%m-%d %H:%M") for ts in timestamps],
        "customer_type": customer_types,
        "item_count": item_counts,
        "order_received_mins": s1,
        "payment_verification_mins": s2,
        "picking_packing_mins": s3,
        "dispatch_mins": s4,
        "total_duration_mins": total_duration,
        "target_sla_mins": target_sla,
        "sla_met": sla_met
    })
    
    return df

def generate_live_orders(seed=101):
    """
    Generates 20 active in-progress orders for the Order Delay Early Warning Radar.
    Includes realistic warning rules: Overdue, At Risk, and On Track.
    """
    np.random.seed(seed)
    
    orders = [
        {"id": "ORD-8801", "customer": "Aarav Sharma", "items": 2, "priority": "High", "stage": "Picking and Packing", "elapsed": 215, "sla": 180},
        {"id": "ORD-8802", "customer": "Priya Patel", "items": 1, "priority": "Normal", "stage": "Payment Verification", "elapsed": 78, "sla": 240},
        {"id": "ORD-8803", "customer": "Rohan Gupta", "items": 6, "priority": "High", "stage": "Picking and Packing", "elapsed": 165, "sla": 180},
        {"id": "ORD-8804", "customer": "Ananya Reddy", "items": 3, "priority": "Normal", "stage": "Dispatch", "elapsed": 190, "sla": 240},
        {"id": "ORD-8805", "customer": "Vikram Singh", "items": 1, "priority": "Normal", "stage": "Order Received", "elapsed": 12, "sla": 240},
        {"id": "ORD-8806", "customer": "Sneha Mukherjee", "items": 4, "priority": "High", "stage": "Picking and Packing", "elapsed": 195, "sla": 180},
        {"id": "ORD-8807", "customer": "Kavita Rao", "items": 2, "priority": "Normal", "stage": "Payment Verification", "elapsed": 32, "sla": 240},
        {"id": "ORD-8808", "customer": "Aditya Verma", "items": 8, "priority": "Normal", "stage": "Picking and Packing", "elapsed": 248, "sla": 240},
        {"id": "ORD-8809", "customer": "Meera Iyer", "items": 1, "priority": "High", "stage": "Dispatch", "elapsed": 110, "sla": 180},
        {"id": "ORD-8810", "customer": "Rahul Deshmukh", "items": 3, "priority": "Normal", "stage": "Order Received", "elapsed": 28, "sla": 240},
        {"id": "ORD-8811", "customer": "Pooja Nair", "items": 5, "priority": "High", "stage": "Payment Verification", "elapsed": 135, "sla": 180},
        {"id": "ORD-8812", "customer": "Arjun Menon", "items": 2, "priority": "Normal", "stage": "Picking and Packing", "elapsed": 140, "sla": 240},
        {"id": "ORD-8813", "customer": "Deepika Joshi", "items": 1, "priority": "Normal", "stage": "Dispatch", "elapsed": 255, "sla": 240},
        {"id": "ORD-8814", "customer": "Siddharth Jain", "items": 3, "priority": "Normal", "stage": "Order Received", "elapsed": 15, "sla": 240},
        {"id": "ORD-8815", "customer": "Tanvi Kulkarni", "items": 2, "priority": "High", "stage": "Picking and Packing", "elapsed": 172, "sla": 180},
        {"id": "ORD-8816", "customer": "Gaurav Bansal", "items": 4, "priority": "Normal", "stage": "Payment Verification", "elapsed": 45, "sla": 240},
        {"id": "ORD-8817", "customer": "Neha Kapoor", "items": 7, "priority": "High", "stage": "Picking and Packing", "elapsed": 230, "sla": 180},
        {"id": "ORD-8818", "customer": "Kunal Chawla", "items": 1, "priority": "Normal", "stage": "Dispatch", "elapsed": 85, "sla": 240},
        {"id": "ORD-8819", "customer": "Divya Sundaram", "items": 2, "priority": "Normal", "stage": "Picking and Packing", "elapsed": 95, "sla": 240},
        {"id": "ORD-8820", "customer": "Manish Tiwari", "items": 3, "priority": "High", "stage": "Dispatch", "elapsed": 178, "sla": 180}
    ]
    
    records = []
    for o in orders:
        elapsed = o["elapsed"]
        sla = o["sla"]
        stage = o["stage"]
        pct_used = round((elapsed / sla) * 100, 1)
        
        # Transparent rule logic
        if elapsed > sla:
            status = "CRITICAL: Overdue"
            reason = f"Exceeded {sla}m deadline by {elapsed - sla}m while still in {stage}."
            badge_color = "red"
        elif pct_used >= 75.0 and stage in ["Order Received", "Payment Verification", "Picking and Packing"]:
            status = "WARNING: At Risk"
            reason = f"{pct_used}% of deadline consumed; still trapped in upstream stage ({stage})."
            badge_color = "amber"
        elif pct_used >= 85.0 and stage == "Dispatch":
            status = "WARNING: At Risk"
            reason = f"At {pct_used}% SLA limit; carrier handover must occur immediately."
            badge_color = "amber"
        else:
            status = "HEALTHY: On Track"
            remaining = sla - elapsed
            reason = f"On schedule. {remaining}m remaining before deadline."
            badge_color = "green"
            
        records.append({
            "order_id": o["id"],
            "customer_name": o["customer"],
            "item_count": o["items"],
            "priority": o["priority"],
            "current_stage": stage,
            "elapsed_mins": elapsed,
            "deadline_mins": sla,
            "sla_consumed_pct": pct_used,
            "status": status,
            "badge_color": badge_color,
            "warning_reason": reason
        })
        
    return pd.DataFrame(records)
