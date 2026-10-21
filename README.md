# ⚡ FlowFix — AI Workflow Bottleneck Detective
> *"Find the bottleneck. Fix the flow."*

**FlowFix** is an interactive web application designed for e-commerce and logistics operations to detect fulfillment delays, identify root causes, simulate process improvements, and provide early warning alerts for orders at risk of missing their dispatch deadlines.

Built for **College Project Expos and Technical Demonstrations**, FlowFix runs 100% locally with **zero external API keys, zero paid services, and zero complex database setup**.

---

## 📁 Project Architecture & File Breakdown

FlowFix is organized into clean, modular, beginner-friendly Python files:

| File | Purpose |
|---|---|
| [`app.py`](app.py) | **Main Web Dashboard**: The Streamlit user interface featuring interactive controls, KPI summary cards, sidebar navigation, and presentation tabs. |
| [`analyzer.py`](analyzer.py) | **Analytics Engine**: Pure mathematical calculations for stage durations, bottleneck severity, the FlowFix Efficiency Score formula, and What-If simulation metrics. |
| [`data_generator.py`](data_generator.py) | **Synthetic Data Generator**: Generates realistic, reproducible order workflow data (250 completed orders and 20 live active orders) with seeded random distributions. |
| [`visualizations.py`](visualizations.py) | **Plotly Chart Builder**: Generates responsive, presentation-grade interactive charts (Horizontal bar charts, Donut charts, Before-vs-After comparison charts, and Status radars). |
| [`recommendations.py`](recommendations.py) | **Diagnostic Knowledge Base**: Contains warehouse operational diagnostics, separating confirmed data facts from unverified hypotheses, with actionable solutions. |
| [`requirements.txt`](requirements.txt) | **Dependency Manifest**: Lists the required Python packages (`streamlit`, `pandas`, `numpy`, `plotly`). |
| [`README.md`](README.md) | **Documentation**: Setup guide for macOS and Windows, expo pitch script, and methodology documentation. |

---

## 🍎 How to Run on macOS (Step-by-Step for Beginners)

Follow these exact steps in your Mac's **Terminal**:

### Step 1: Open Terminal
1. Press `Cmd + Space` on your keyboard to open **Spotlight Search**.
2. Type `Terminal` and press **Enter** (Return).

---

### Step 2: Navigate to the Project Folder
In the Terminal window, paste this command and press **Enter**:
```bash
cd ~/Downloads/"project expo"
```
*(Tip: You can confirm you are in the right folder by typing `pwd` and pressing Enter; it will show `/Users/<your-name>/Downloads/project expo`).*

---

### Step 3: Check Python & Command Line Tools
Type the following command and press **Enter**:
```bash
python3 --version
```
- **If you see a version** like `Python 3.10.x`, `3.11.x`, or `3.12.x`: you are good to proceed to Step 4!
- **If a pop-up window appears** saying *"The 'xcode-select' command requires the command line developer tools. Would you like to install the tools now?"*:
  1. Click **Install** on the pop-up and accept the license.
  2. Wait 2-3 minutes for macOS to finish downloading the tools.
  3. Alternatively, if you prefer not to wait for Xcode tools, download and install the official Python package from [python.org/downloads/macos](https://www.python.org/downloads/macos/).

---

### Step 4: Create and Activate a Virtual Environment
A virtual environment keeps your project packages isolated and prevents permission errors.

1. Create the virtual environment folder:
   ```bash
   python3 -m venv venv
   ```
2. Activate it:
   ```bash
   source venv/bin/activate
   ```
*(Once activated, you will see `(venv)` at the beginning of your terminal line).*

---

### Step 5: Install Required Packages
With `(venv)` active, install Streamlit, Pandas, NumPy, and Plotly:
```bash
pip install -r requirements.txt
```

---

### Step 6: Launch the FlowFix Web Application
Run:
```bash
streamlit run app.py
```

---

### Step 7: Open in Your Browser
Streamlit will automatically open Safari or Chrome. If it does not open automatically, open your browser and navigate to:
```text
http://localhost:8501
```
*(To stop the app anytime, press `Ctrl + C` in your Terminal).*

---

## 🪟 Alternative: Running on Windows
If you transfer this project to a Windows laptop for your expo booth:
1. Open **Command Prompt (`cmd`)** and navigate to the project directory:
   ```cmd
   cd "C:\path\to\project expo"
   ```
2. Create and activate virtual environment:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies and run:
   ```cmd
   pip install -r requirements.txt
   streamlit run app.py
   ```

---

## 🎯 College Expo Judge Demonstration Script (3-Minute Walkthrough)

When presenting to professors or industry judges, follow this step-by-step demo:

### Step 1: The Problem & Baseline Analysis (1 Minute)
1. Point to the **Top Header**: Highlight the tagline *"Find the bottleneck. Fix the flow."* and note that the app analyzes order fulfillment across 4 stages: **Order Received ➔ Payment Verification ➔ Picking and Packing ➔ Dispatch**.
2. Show the **Summary Metric Cards**:
   - Current Cycle Time: ~**217.3 mins** (3.6 hours).
   - Bottleneck Badge: **Picking and Packing** is highlighted in red.
3. Open Section **1. 📊 Bottleneck Detective**:
   - Show the **Average Duration Chart** and **Donut Share Chart**.
   - Explain: *"Judges, Picking & Packing accounts for 65.4% of total order lead time. Even if dispatch or payment verification are optimized, orders remain trapped in warehouse picking."*

### Step 2: Interactive What-If Time Machine (1 Minute)
1. Switch to Section **2. ⏳ What-If Time Machine**.
2. Move the **Picking & Packing Reduction Slider** on the sidebar from `0` to `38 mins`.
3. Watch the screen update **instantly**:
   - The **Before vs. After Grouped Bar Chart** visibly drops.
   - Cycle time reduces by **22.1%**.
   - Explain: *"With an operational fix like Wave Picking and SKU velocity zoning, we cut 38 minutes per order. Across 250 daily orders, this frees up ~158 labor hours every day."*

### Step 3: Root Cause & Early Warning Radar (1 Minute)
1. Open Section **3. 🩺 Root Cause Detective**:
   - Explain how FlowFix differentiates **Confirmed Data Facts** (measured order times) from **Unverified Hypotheses** (walking distances, missing bin labels) so management knows what to inspect on-site.
2. Open Section **4. 🚨 Order Delay Early Warning**:
   - Show the **Live Order Radar Scatter Plot**.
   - Point out orders marked **CRITICAL: Overdue** (red) and **WARNING: At Risk** (amber).
   - Explain the explainable rule: *"Orders at 75%+ of their SLA threshold still in picking are flagged early, before customer service receives a complaint."*

---

## 📐 Formulas & Methodology

### 1. FlowFix Efficiency Score (0 to 100)
FlowFix uses a deterministic, explainable multi-factor formula rather than an arbitrary score:

$$\text{Efficiency Score} = (0.40 \times \text{SLA Compliance}) + (0.35 \times \text{Balance Index}) + (0.25 \times \text{Velocity Index})$$

- **SLA Compliance (40% Weight):** % of orders dispatched within their promised delivery SLA (180 mins for Express, 240 mins for Standard).
- **Workflow Balance Index (35% Weight):** Measures whether workload flows evenly across all 4 stages:
  $$\text{Balance} = 100 - (\text{Max Stage Share}\% - 25\%) \times 1.8$$
  *(In an ideal pipeline, each stage takes ~25% of the time. When one stage consumes 65%+, Balance drops).*
- **Velocity Index (25% Weight):** Compares average turnaround speed against an industry standard benchmark ($150\text{ mins}$):
  $$\text{Velocity} = \min\left(100, \left(\frac{150}{\text{Total Average Minutes}}\right) \times 100\right)$$

### 2. Time & Financial Savings
- **Time Saved Per Order:** $\text{Baseline Average Mins} - \text{Simulated Average Mins}$
- **Daily Labor Hours Saved:** $(\text{Time Saved Per Order} \times \text{Daily Orders}) \div 60$
- **Estimated Annual Financial Unlock:** $\text{Daily Hours Saved} \times 365 \times \text{Hourly Wage Rate}$

---

## ⚖️ Honest Limitations to Disclose During Presentation

When judges ask for critical evaluation and future scope, present these honest limitations:

1. **Stage Milestone Granularity:**
   - *Current Limitation:* FlowFix calculates durations from stage timestamps (e.g. pick started to pick completed).
   - *Future Work:* Integrating indoor IoT beacons or RFID tags would allow sub-stage timing (e.g., picker walking transit vs searching vs packing).
2. **Synthetic Sample Data:**
   - *Current Limitation:* The demonstration uses statistically realistic sample data with fixed seeds for reliable offline demos.
   - *Future Work:* Building direct connectors for Shopify, WooCommerce, and ShipStation webhooks.
3. **Financial Savings Nature:**
   - *Disclaimer:* Operational time saved does not automatically lower payroll unless overtime or headcount is reduced. Its primary real-world value is **increasing order capacity without hiring more staff** and **preventing customer SLA breach penalties**.

---

## 🛠️ Technology Stack
- **Python 3.9+**
- **Streamlit**: Modern interactive web framework
- **Pandas & NumPy**: Data processing and statistical analysis
- **Plotly**: Presentation-grade interactive data visualizations
- **Zero External APIs**: 100% offline, cross-platform (macOS & Windows), and cost-free execution
