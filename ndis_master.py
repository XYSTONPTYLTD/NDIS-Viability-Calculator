import streamlit as st
import datetime
from datetime import timedelta
import plotly.express as px
import pandas as pd
import pytz

# ==============================================================================
# NDIS VIABILITY MASTER - AUSTRALIAN EDITION (2025)
# Built by Chas Walker | Xyston.com.au
# Features: Clean UI, Fixed Sidebar, Fancy Donation Button
# ==============================================================================

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="NDIS Master | Xyston",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# 2. TIMEZONE SETUP (Perth/Australia)
try:
    perth_tz = pytz.timezone('Australia/Perth')
    today = datetime.datetime.now(perth_tz).date()
except:
    today = datetime.date.today()

# 3. RATES DATABASE (2025)
RATES = {
    "Level 2: Coordination of Supports": 100.14,
    "Level 3: Specialist Support Coordination": 190.41
}

# ==============================================================================
# SIDEBAR - INPUTS
# ==============================================================================
with st.sidebar:
    # --- BRANDING (Clean Text - No Broken Images) ---
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="font-size: 3em; margin: 0;">🛡️</h1>
            <h2 style="font-weight: 800; margin: 0; color: #fafafa;">XYSTON</h2>
            <p style="font-size: 0.8em; opacity: 0.7;">NDIS Master Calc v2025.3</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    st.divider()

    st.header("1. Plan Settings")
    
    # Rate Selector
    support_type = st.selectbox("Support Level", list(RATES.keys()))
    default_rate = RATES[support_type]
    hourly_rate = st.number_input("Hourly Rate ($)", value=default_rate, step=0.01)

    st.divider()
    
    st.header("2. Critical Dates")
    # Date Inputs with Australian Format (DD/MM/YYYY)
    plan_start = st.date_input(
        "Plan Start Date", 
        value=today - timedelta(weeks=12),
        format="DD/MM/YYYY"
    )
    plan_end = st.date_input(
        "Plan End Date", 
        value=today + timedelta(weeks=40),
        format="DD/MM/YYYY"
    )

    # Date Validation
    if plan_end <= today:
        st.error("⚠️ Plan End Date must be in the future.")
        st.stop()
        
    days_remaining = (plan_end - today).days
    weeks_remaining = days_remaining / 7
    
    st.caption(f"📅 Today is {today.strftime('%d/%m/%Y')}. **{weeks_remaining:.1f} weeks** remaining.")

    st.divider()

    st.header("3. Portal Financials")
    total_budget = st.number_input("Total Original Budget ($)", value=18000.0, step=100.0)
    current_balance = st.number_input(
        "Current Portal Balance ($)", 
        value=14500.0, 
        step=50.0, 
        help="Enter the EXACT amount currently available in the PRODA portal."
    )

    st.divider()
    
    st.header("4. Your Billing")
    hours_per_week = st.number_input("Planned Hours/Week", value=1.5, step=0.1)
    
    st.markdown("---")
    
    # --- DONATION BUTTON (FANCY) ---
    st.markdown(
        """
        <div style="text-align: center;">
            <p style="font-size: 0.9em; color: #666;">Find this tool useful?</p>
            <a href="https://www.buymeacoffee.com/h0m1ez187" target="_blank">
                <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 50px !important;width: 180px !important;" >
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==============================================================================
# LOGIC CORE
# ==============================================================================

# 1. Costs
weekly_cost = hours_per_week * hourly_rate

# 2. Runway Calculation
if weekly_cost > 0:
    runway_weeks = current_balance / weekly_cost
else:
    runway_weeks = 999 

depletion_date = today + timedelta(days=int(runway_weeks * 7))

# 3. Gap Analysis
required_to_finish = weekly_cost * weeks_remaining
surplus_shortfall = current_balance - required_to_finish
spent_so_far = max(0, total_budget - current_balance)
utilisation_pct = (spent_so_far / total_budget) * 100 if total_budget > 0 else 0

# 4. Status Determination
buffer_ratio = runway_weeks / weeks_remaining if weeks_remaining > 0 else 0

if buffer_ratio >= 1.2:
    status_title = "🟢 PLATINUM CLIENT"
    status_desc = "Safe Surplus. Excellent viability."
    status_colour = "#00cc66" # Green
    bg_colour = "rgba(0, 204, 102, 0.1)"
elif buffer_ratio >= 1.0:
    status_title = "🟢 VIABLE (ON TRACK)"
    status_desc = "Fully funded for the remaining time."
    status_colour = "#66ff66" # Light Green
    bg_colour = "rgba(102, 255, 102, 0.1)"
elif buffer_ratio >= 0.85:
    status_title = "🟡 MARGINAL (MONITOR)"
    status_desc = "Tight budget. Watch billing closely."
    status_colour = "#ffd700" # Gold
    bg_colour = "rgba(255, 215, 0, 0.1)"
else:
    status_title = "🔴 HIGH RISK / NON-VIABLE"
    status_desc = "Insufficient funds. Immediate action required."
    status_colour = "#ff4444" # Red
    bg_colour = "rgba(255, 68, 68, 0.1)"

# ==============================================================================
# MAIN DASHBOARD UI
# ==============================================================================

# Header
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.title("🛡️ NDIS Viability Master")
    st.caption(f"Fail-Safe Analysis • {support_type.split(':')[0]}")
with col_head2:
    st.markdown("#### **Xyston**")

st.divider()

# Status Banner
st.markdown(f"""
    <div style="
        border: 2px solid {status_colour}; 
        border-radius: 12px; 
        padding: 20px; 
        background-color: {bg_colour}; 
        text-align: center; 
        margin-bottom: 25px;">
        <h2 style="color: {status_colour}; margin: 0; font-weight: 800;">{status_title}</h2>
        <p style="margin-top: 8px; font-size: 1.1em; opacity: 0.9;">{status_desc}</p>
    </div>
""", unsafe_allow_html=True)

# Metrics Row
m1, m2, m3, m4 = st.columns(4)
m1.metric("Current Balance", f"${current_balance:,.2f}", help="From Portal")
m2.metric("Weekly Cost", f"${weekly_cost:,.2f}", f"{hours_per_week} hrs/wk")
m3.metric("Depletion Date", depletion_date.strftime("%d/%m/%Y"), 
          delta=f"{abs((depletion_date - plan_end).days)} days {'early' if depletion_date < plan_end else 'buffer'}",
          delta_color="inverse" if depletion_date < plan_end else "normal")
m4.metric("End Result", f"${surplus_shortfall:,.2f}", 
          "Surplus" if surplus_shortfall > 0 else "Shortfall",
          delta_color="normal" if surplus_shortfall < 0 else "inverse")

# ==============================================================================
# CHARTS & VISUALS
# ==============================================================================
st.subheader("📊 Financial Trajectory")

tab1, tab2 = st.tabs(["Burn-Down Chart", "Budget Breakdown"])

with tab1:
    chart_weeks = int(weeks_remaining) + 4
    dates = [today + timedelta(weeks=w) for w in range(chart_weeks + 1)]
    
    projected_balance = [max(0, current_balance - (w * weekly_cost)) for w in range(chart_weeks + 1)]
    
    if weeks_remaining > 0:
        ideal_burn_rate = current_balance / weeks_remaining
        ideal_balance = [max(0, current_balance - (w * ideal_burn_rate)) for w in range(chart_weeks + 1)]
    else:
        ideal_balance = [0] * (chart_weeks + 1)

    df_chart = pd.DataFrame({
        "Date": dates * 2,
        "Balance": projected_balance + ideal_balance,
        "Scenario": ["Your Trajectory"] * len(dates) + ["Break-Even Path"] * len(dates)
    })

    fig = px.line(df_chart, x="Date", y="Balance", color="Scenario",
                  color_discrete_map={"Your Trajectory": status_colour, "Break-Even Path": "#808080"})
    
    # Australian Date Format for Hover
    fig.update_xaxes(tickformat="%d/%m/%Y")
    
    fig.add_vline(x=datetime.datetime.combine(plan_end, datetime.time.min).timestamp() * 1000, 
                  line_dash="dot", line_color="white", annotation_text="Plan End")
    
    fig.update_layout(height=350, hovermode="x unified", margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    col_pie1, col_pie2 = st.columns([1, 2])
    with col_pie1:
        fig_pie = px.pie(
            values=[spent_so_far, current_balance], 
            names=["Already Used", "Remaining"],
            color_discrete_sequence=["#333333", status_colour],
            hole=0.4
        )
        fig_pie.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=10), height=250)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col_pie2:
        st.markdown("#### Budget Health")
        st.progress(min(utilisation_pct / 100, 1.0))
        st.caption(f"You have utilised **{utilisation_pct:.1f}%** of the original total budget.")
        
        if surplus_shortfall < 0:
            st.error(f"⚠️ You are projected to be short by **${abs(surplus_shortfall):,.2f}**.")
        else:
            st.success(f"✅ You are projected to have a surplus of **${surplus_shortfall:,.2f}**.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        © 2025 Xyston Pty Ltd | NDIS Viability Calculator<br>
        Built by Chas Walker | <a href='https://www.xyston.com.au'>www.xyston.com.au</a><br><br>
        <a href="https://www.buymeacoffee.com/h0m1ez187" target="_blank" style="text-decoration: none; color: #FFDD00; font-weight: bold;">
            ☕ Buy Me a Coffee
        </a>
    </div>
    """, 
    unsafe_allow_html=True
)
