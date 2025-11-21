import streamlit as st
import datetime
from datetime import timedelta
import plotly.express as px
import pandas as pd
import pytz # Required for accurate Perth time on Cloud servers

# ==============================================================================
# NDIS VIABILITY MASTER - PRODUCTION EDITION (2025)
# Built by Chas Walker | Xyston.com.au
# Features: Timezone-aware, Mobile Responsive, Fail-Safe Logic
# ==============================================================================

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="NDIS Master | Xyston",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# 2. TIMEZONE SETUP (Critical for Cloud Deployment)
# Streamlit Cloud servers run on UTC. We must force Perth time.
try:
    perth_tz = pytz.timezone('Australia/Perth')
    today = datetime.datetime.now(perth_tz).date()
except:
    # Fallback if pytz fails for any reason
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
    st.header("1. Plan Settings")
    
    # Rate Selector
    support_type = st.selectbox("Support Level", list(RATES.keys()))
    default_rate = RATES[support_type]
    hourly_rate = st.number_input("Hourly Rate ($)", value=default_rate, step=0.01)

    st.divider()
    
    st.header("2. Critical Dates")
    # Date Inputs
    # Default Plan Start = 3 months ago, Plan End = 9 months from now
    plan_start = st.date_input("Plan Start Date", value=today - timedelta(weeks=12))
    plan_end = st.date_input("Plan End Date", value=today + timedelta(weeks=40))

    # Date Validation
    if plan_end <= today:
        st.error("⚠️ Plan End Date must be in the future.")
        st.stop()
        
    days_remaining = (plan_end - today).days
    weeks_remaining = days_remaining / 7
    st.caption(f"📅 Today is {today.strftime('%d %b')}. **{weeks_remaining:.1f} weeks** remaining.")

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

# ==============================================================================
# LOGIC CORE
# ==============================================================================

# 1. Costs
weekly_cost = hours_per_week * hourly_rate

# 2. Runway Calculation (Fail-Safe)
if weekly_cost > 0:
    runway_weeks = current_balance / weekly_cost
else:
    runway_weeks = 999 # Infinite runway if not spending

depletion_date = today + timedelta(days=int(runway_weeks * 7))

# 3. Gap Analysis
required_to_finish = weekly_cost * weeks_remaining
surplus_shortfall = current_balance - required_to_finish

# 4. Status Determination
buffer_ratio = runway_weeks / weeks_remaining if weeks_remaining > 0 else 0

if buffer_ratio >= 1.2:
    status_title = "🟢 PLATINUM CLIENT"
    status_desc = "Safe Surplus. Excellent viability."
    status_color = "#00cc66" # Green
    bg_color = "rgba(0, 204, 102, 0.1)"
elif buffer_ratio >= 1.0:
    status_title = "🟢 VIABLE (ON TRACK)"
    status_desc = "Fully funded for the remaining time."
    status_color = "#66ff66" # Light Green
    bg_color = "rgba(102, 255, 102, 0.1)"
elif buffer_ratio >= 0.85:
    status_title = "🟡 MARGINAL (MONITOR)"
    status_desc = "Tight budget. Watch billing closely."
    status_color = "#ffd700" # Gold
    bg_color = "rgba(255, 215, 0, 0.1)"
else:
    status_title = "🔴 HIGH RISK / NON-VIABLE"
    status_desc = "Insufficient funds. Immediate action required."
    status_color = "#ff4444" # Red
    bg_color = "rgba(255, 68, 68, 0.1)"

# ==============================================================================
# MAIN DASHBOARD UI
# ==============================================================================

# Header
col_head1, col_head2 = st.columns([4, 1])
with col_head1:
    st.title("🛡️ NDIS Viability Master")
    st.caption(f"Fail-Safe Analysis • {support_type.split(':')[0]}")
with col_head2:
    # Display Author info in a clean way
    st.markdown("**Xyston**")
    st.caption("v2025.1")

st.divider()

# Status Banner (CSS Injected for nice styling)
st.markdown(f"""
    <div style="
        border: 2px solid {status_color}; 
        border-radius: 12px; 
        padding: 20px; 
        background-color: {bg_color}; 
        text-align: center; 
        margin-bottom: 25px;">
        <h2 style="color: {status_color}; margin: 0; font-weight: 800;">{status_title}</h2>
        <p style="margin-top: 8px; font-size: 1.1em; opacity: 0.9;">{status_desc}</p>
    </div>
""", unsafe_allow_html=True)

# Metrics Row
m1, m2, m3, m4 = st.columns(4)
m1.metric("Current Balance", f"${current_balance:,.2f}", help="From Portal")
m2.metric("Weekly Cost", f"${weekly_cost:,.2f}", f"{hours_per_week} hrs/wk")
m3.metric("Depletion Date", depletion_date.strftime("%d %b %Y"), 
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
    # 1. Burn Down Data Construction
    # We create points for every week from Now until Plan End + 4 weeks (for buffer visibility)
    chart_weeks = int(weeks_remaining) + 4
    dates = [today + timedelta(weeks=w) for w in range(chart_weeks + 1)]
    
    # Projected Balance
    projected_balance = [max(0, current_balance - (w * weekly_cost)) for w in range(chart_weeks + 1)]
    
    # Ideal Balance (Target)
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

    # Plotly Chart
    fig = px.line(df_chart, x="Date", y="Balance", color="Scenario",
                  color_discrete_map={"Your Trajectory": status_color, "Break-Even Path": "#808080"})
    
    # Add Plan End Line
    fig.add_vline(x=datetime.datetime.combine(plan_end, datetime.time.min).timestamp() * 1000, 
                  line_dash="dot", line_color="white", annotation_text="Plan End")
    
    fig.update_layout(height=350, hovermode="x unified", margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    col_pie1, col_pie2 = st.columns([1, 2])
    with col_pie1:
        # Pie Chart
        spent = max(0, total_budget - current_balance)
        fig_pie = px.pie(
            values=[spent, current_balance], 
            names=["Already Used", "Remaining"],
            color_discrete_sequence=["#333333", status_color],
            hole=0.4
        )
        fig_pie.update_layout(showlegend=False, margin=dict(l=0, r=0, t=10, b=10), height=250)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col_pie2:
        st.markdown("#### Budget Health")
        utilization = (spent / total_budget) * 100 if total_budget > 0 else 0
        st.progress(min(utilization / 100, 1.0))
        st.caption(f"You have used **{utilization:.1f}%** of the original total budget.")
        
        if surplus_shortfall < 0:
            st.error(f"⚠️ You are projected to be short by **${abs(surplus_shortfall):,.2f}**.")
        else:
            st.success(f"✅ You are projected to have a surplus of **${surplus_shortfall:,.2f}**.")

# ==============================================================================
# AI RECOMMENDATION ENGINE
# ==============================================================================
st.markdown("---")
st.subheader("🤖 AI Second Opinion")

# Recommendation Logic
break_even_hours = current_balance / weeks_remaining / hourly_rate if weeks_remaining > 0 else 0

if surplus_shortfall < -500:
    adv_icon = "🛑"
    adv_title = "CRITICAL ACTION REQUIRED"
    adv_msg = f"""
    You are burning funding too fast. The plan will run dry on **{depletion_date.strftime('%d %b %Y')}**.
    
    **You must do one of the following:**
    1. **Reduce Billable Hours:** Drop to **{break_even_hours:.2f} hrs/week** immediately.
    2. **Review:** If the participant needs {hours_per_week} hrs/week, lodge a Review of Reviewable Decisions (s48) or CoC immediately.
    """
    adv_style = "error"

elif surplus_shortfall > 2500:
    adv_icon = "💎"
    adv_title = "UNDERSERVICING DETECTED"
    adv_msg = f"""
    You have a significant surplus. You are currently leaving **${surplus_shortfall:,.2f}** on the table.
    
    **Strategy:**
    * You can safely increase support to **{break_even_hours:.1f} hrs/week**.
    * Consider using funds for additional provider meetings, reporting, or allied health coordination.
    """
    adv_style = "info"

else:
    adv_icon = "✅"
    adv_title = "PERFECTLY BALANCED"
    adv_msg = f"""
    Your current billing cadence is sustainable. You are tracking to finish the plan with a minor variance of **${surplus_shortfall:,.2f}**.
    
    **Strategy:** Maintain current schedule. Monitor monthly.
    """
    adv_style = "success"

# Display Advice
with st.container():
    if adv_style == "error":
        st.error(f"**{adv_icon} {adv_title}**\n\n{adv_msg}")
    elif adv_style == "info":
        st.info(f"**{adv_icon} {adv_title}**\n\n{adv_msg}")
    else:
        st.success(f"**{adv_icon} {adv_title}**\n\n{adv_msg}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        © 2025 Xyston Pty Ltd | NDIS Viability Calculator Master Edition<br>
        Built by Chas Walker | <a href='https://www.xyston.com.au'>www.xyston.com.au</a>
    </div>
    """, 
    unsafe_allow_html=True
)
