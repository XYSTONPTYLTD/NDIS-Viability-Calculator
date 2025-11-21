import streamlit as st
import datetime
from datetime import timedelta
import plotly.express as px
import pandas as pd

# ==============================================================================
# NDIS CALCULATOR - FAIL-SAFE EDITION (2025)
# Built by Chas Walker | Xyston.com.au
# Focus: 100% Accuracy via "Portal Truth" Logic. No manual week counting.
# ==============================================================================

st.set_page_config(page_title="NDIS Viability Master | Xyston", layout="wide", page_icon="🛡️")

# --- BRANDING & HEADER ---
col_brand, col_logo = st.columns([4, 1])
with col_brand:
    st.title("🛡️ NDIS Viability Master (Fail-Safe)")
    st.markdown("**The Zero-Error Tool for Independent Coordinators**")
    st.caption("Enter the Plan End Date and Portal Balance. We do the rest.")

with st.expander("⚠️ Disclaimer & Authorship"):
    st.markdown("""**Built by Chas Walker (Xyston.com.au).** For planning purposes only. Use at your own risk based on your own inputs.""")

st.markdown("---")

# --- 2025 RATE DATA (Source of Truth) ---
RATES = {
    "Level 2: Coordination of Supports": 100.14,
    "Level 3: Specialist Support Coordination": 190.41
}

# ==============================================================================
# 1. THE "FAIL-SAFE" SIDEBAR INPUTS
# ==============================================================================
st.sidebar.header("1. The Essentials")

# A. SELECT RATE (Prevents wrong billing math)
support_type = st.sidebar.selectbox("Support Level", list(RATES.keys()))
default_rate = RATES[support_type]
hourly_rate = st.sidebar.number_input("Your Hourly Rate ($)", value=default_rate, step=0.01)

# B. PLAN DATES (Prevents "Weeks Remaining" math errors)
# We ask for dates because they are written on the plan. We calculate the weeks.
today = datetime.date.today()
st.sidebar.subheader("2. Critical Dates")
plan_start = st.sidebar.date_input("Plan Start Date", value=today - timedelta(weeks=12))
plan_end = st.sidebar.date_input("Plan End Date", value=today + timedelta(weeks=40))

# FAIL-SAFE CALCULATION: Weeks Remaining
if plan_end <= today:
    st.error("Error: Plan End Date must be in the future.")
    st.stop()

days_remaining = (plan_end - today).days
weeks_remaining = days_remaining / 7

st.sidebar.info(f"📅 **{days_remaining} days** ({weeks_remaining:.1f} weeks) remaining.")

# C. FINANCIALS (The "Portal Truth")
st.sidebar.subheader("3. Financials (Portal Truth)")
total_budget = st.sidebar.number_input("Total Original Budget ($)", value=18000.0, step=100.0, help="The total amount originally allocated.")
current_balance = st.sidebar.number_input("Current Portal Balance ($)", value=14500.0, step=50.0, help="The EXACT amount showing in the NDIS portal today.")

# D. YOUR PLAN
st.sidebar.subheader("4. Your Action")
hours_per_week = st.sidebar.number_input("Planned Hours Per Week", value=1.5, step=0.1)

# ==============================================================================
# 2. THE CALCULATIONS (Hidden Complexity)
# ==============================================================================

# 1. Burn Rate
weekly_cost = hours_per_week * hourly_rate

# 2. Runway (The "Line in the Sand" Calculation)
# We ignore past history. We only care about: Can [Current Balance] survive [Weeks Remaining]?
if weekly_cost > 0:
    runway_weeks = current_balance / weekly_cost
else:
    runway_weeks = 999

depletion_date = today + timedelta(days=int(runway_weeks * 7))

# 3. The Gap
required_to_finish = weekly_cost * weeks_remaining
surplus_shortfall = current_balance - required_to_finish

# 4. Status Logic (Traffic Light)
# Buffer: How many extra weeks of funding do we have vs time left?
buffer_weeks = runway_weeks - weeks_remaining

if runway_weeks >= weeks_remaining * 1.2:
    status = "🟢 PLATINUM CLIENT (Safe Surplus)"
    color = "#00cc66"
elif runway_weeks >= weeks_remaining:
    status = "🟢 VIABLE (On Track)"
    color = "#66ff66"
elif runway_weeks >= weeks_remaining - 2:
    status = "🟡 TIGHT (Monitor Closely)"
    color = "#ffff00"
else:
    status = "🔴 NON-VIABLE (Immediate Action Req)"
    color = "#ff4444"

# ==============================================================================
# 3. THE DASHBOARD
# ==============================================================================

# BIG VISUAL STATUS
st.markdown(f"""
    <div style="border: 2px solid {color}; border-radius: 10px; padding: 10px; background-color: {color}20; text-align: center;">
        <h1 style="color: {color}; margin: 0;">{status}</h1>
        <p style="font-size: 1.2em; margin-top: 5px;">
            You have <b>{runway_weeks:.1f} weeks</b> of funding for <b>{weeks_remaining:.1f} weeks</b> of time.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### 💼 Financial Snapshot")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Funds Available Now", f"${current_balance:,.2f}", "Source: Portal")
m2.metric("Your Weekly Bill", f"${weekly_cost:,.2f}", f"{hours_per_week} hrs @ ${hourly_rate:.0f}")
m3.metric("Depletion Date", depletion_date.strftime("%d %b %Y"), f"Plan ends {plan_end.strftime('%d %b')}")
m4.metric("Outcome at Plan End", f"${surplus_shortfall:,.2f}", "Surplus" if surplus_shortfall > 0 else "Shortfall", 
          delta_color="normal" if surplus_shortfall < 0 else "inverse")

# ==============================================================================
# 4. VISUAL PROOF (Burn Down)
# ==============================================================================

c1, c2 = st.columns([1, 2])

with c1:
    st.markdown("#### 📊 Budget Usage")
    # Simple Pie: What is gone vs What is left
    spent = total_budget - current_balance
    fig_pie = px.pie(values=[spent, current_balance], names=["Already Spent", "Available Now"], 
                     color_discrete_sequence=["#ffaaaa", "#aaffaa"], hole=0.4)
    fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=250)
    fig_pie.add_annotation(text=f"${current_balance/1000:.1f}k<br>Left", showarrow=False, font_size=15)
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    st.markdown("#### 📉 The Trajectory")
    # Data for chart
    x_weeks = list(range(int(weeks_remaining) + 4)) # Go a bit past end date
    dates = [today + timedelta(weeks=w) for w in x_weeks]
    
    # Projected Balance Line
    y_balance = [max(0, current_balance - (w * weekly_cost)) for w in x_weeks]
    
    df_chart = pd.DataFrame({"Date": dates, "Balance": y_balance})
    
    fig = px.line(df_chart, x="Date", y="Balance", title="Projected Funding Depletion")
    fig.update_traces(line_color=color, line_width=3)
    
    # Add Plan End Vertical Line
    fig.add_vline(x=datetime.datetime.combine(plan_end, datetime.time.min).timestamp() * 1000, 
                  line_dash="dot", annotation_text="Plan End")
    
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# 5. AI SECOND OPINION (Plain English)
# ==============================================================================

st.markdown("---")
st.subheader("🤖 The AI Second Opinion")

# Fail-Safe Advice Logic
if surplus_shortfall < -500:
    advice_header = "⚠️ DANGER: You are burning too hot."
    advice_body = f"""
    At **{hours_per_week} hours/week**, this participant will run out of money on **{depletion_date.strftime('%d %B')}**—which is **{abs(buffer_weeks):.1f} weeks EARLY**.
    
    **Corrective Action:**
    1. You must reduce billing to **{(current_balance / weeks_remaining / hourly_rate):.2f} hours/week** to break even.
    2. Or, if the client needs this level of support, you must apply for a review immediately.
    """
elif surplus_shortfall > 2000:
    advice_header = "💎 OPPORTUNITY: You are under-servicing."
    advice_body = f"""
    You have a large surplus of **${surplus_shortfall:,.2f}**. If you continue at this rate, you will return money to the NDIA.
    
    **Strategy:**
    * You can safely increase support to **{(current_balance / weeks_remaining / hourly_rate):.1f} hours/week**.
    * Use this funding for extra reports, provider meetings, or capacity building.
    """
else:
    advice_header = "✅ ON TRACK: Perfect Balance."
    advice_body = f"""
    Your billing rate aligns perfectly with the remaining plan duration. You will finish the plan with approximately **${surplus_shortfall:,.2f}** remaining.
    """

st.info(f"**{advice_header}**\n\n{advice_body}")

st.caption("© 2025 Xyston | Fail-Safe NDIS Calculator")
