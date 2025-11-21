import streamlit as st
import datetime
from datetime import timedelta
import plotly.express as px
import pandas as pd
import pytz
import os
import google.generativeai as genai

# ==============================================================================
# CONFIGURATION & ASSETS
# ==============================================================================
st.set_page_config(
    page_title="NDIS Master | Xyston",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# Custom CSS for that "Pro" look
st.markdown("""
<style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    .stMetric { background-color: #0e1117; padding: 10px; border-radius: 5px; border: 1px solid #262730; }
    .status-banner { padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; border: 2px solid; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# UTILITIES
# ==============================================================================
def get_ai_analysis(api_key, context_data):
    """Fetches a professional report from Google Gemini."""
    if not api_key:
        return "⚠️ API Key missing. Please add it to Streamlit Secrets or sidebar."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Act as a Senior NDIS Support Coordinator (Australia). 
        Write a concise 'Viability & Strategy Note' (max 200 words) for a participant file based on this live data:
        
        - **Status:** {context_data['status']}
        - **Weeks Remaining in Plan:** {context_data['weeks_remaining']:.1f}
        - **Current Funds:** ${context_data['balance']:,.2f}
        - **Burn Rate:** ${context_data['weekly_cost']:,.2f}/week
        - **Projected Outcome:** ${context_data['surplus_shortfall']:,.2f} ({'Surplus' if context_data['surplus_shortfall'] > 0 else 'Shortfall'})
        
        Provide 3 clear, actionable strategic dot points for the coordinator to manage this specific financial trajectory. 
        Tone: Professional, risk-aware, Australian English.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error generating report: {str(e)}"

# Timezone Setup
try:
    perth_tz = pytz.timezone('Australia/Perth')
    today = datetime.datetime.now(perth_tz).date()
except:
    today = datetime.date.today()

# Rates
RATES = {
    "Level 2: Coordination of Supports": 100.14,
    "Level 3: Specialist Support Coordination": 190.41
}

# ==============================================================================
# SIDEBAR
# ==============================================================================
with st.sidebar:
    # BRANDING
    st.markdown("""
        <div style="text-align: center; margin-bottom: 10px;">
            <h1 style="font-size: 3rem; margin:0;">🛡️</h1>
            <h2 style="font-weight: 900; letter-spacing: 2px; margin:0;">XYSTON</h2>
            <p style="font-size: 0.8rem; opacity: 0.7; font-family: monospace;">NDIS Master v2025.4</p>
        </div>
        <hr style="margin: 10px 0;">
    """, unsafe_allow_html=True)

    # API KEY HANDLING (Secrets or Input)
    api_key = st.secrets.get("GEMINI_API_KEY", None)
    if not api_key:
        with st.expander("🔐 AI Settings (Optional)"):
            api_key = st.text_input("Enter Google API Key", type="password")

    # INPUTS
    st.markdown("#### 1. Setup")
    support_type = st.selectbox("Support Level", list(RATES.keys()))
    hourly_rate = st.number_input("Hourly Rate ($)", value=RATES[support_type], step=0.01)

    st.markdown("#### 2. Time")
    mode = st.radio("Input Mode", ["Dates", "Weeks"], horizontal=True, label_visibility="collapsed")
    
    if mode == "Dates":
        plan_end = st.date_input("Plan End Date", value=today + timedelta(weeks=40), format="DD/MM/YYYY")
        if plan_end <= today:
            st.error("End date must be future.")
            st.stop()
        days_remaining = (plan_end - today).days
        weeks_remaining = days_remaining / 7
    else:
        weeks_remaining = st.number_input("Weeks Remaining", value=40.0, step=0.5)
        days_remaining = int(weeks_remaining * 7)
        plan_end = today + timedelta(days=days_remaining)

    st.caption(f"📅 **{weeks_remaining:.1f} weeks** remaining")

    st.markdown("#### 3. Money (Portal Truth)")
    total_budget = st.number_input("Original Budget ($)", value=18000.0, step=100.0)
    current_balance = st.number_input("Current Portal Balance ($)", value=14500.0, step=50.0)

    st.markdown("#### 4. Billing")
    hours_per_week = st.number_input("Planned Hours/Week", value=1.5, step=0.1)

    st.markdown("---")
    st.markdown("""
        <div style="text-align: center;">
            <a href="https://www.buymeacoffee.com/h0m1ez187" target="_blank">
                <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 150px !important;" >
            </a>
        </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# LOGIC ENGINE
# ==============================================================================
weekly_cost = hours_per_week * hourly_rate
runway_weeks = current_balance / weekly_cost if weekly_cost > 0 else 999
depletion_date = today + timedelta(days=int(runway_weeks * 7))

required_to_finish = weekly_cost * weeks_remaining
surplus_shortfall = current_balance - required_to_finish
buffer_weeks = runway_weeks - weeks_remaining

# Status Logic
if runway_weeks >= weeks_remaining * 1.2:
    status = "PLATINUM CLIENT"
    color = "#10b981" # Emerald
    bg = "rgba(16, 185, 129, 0.1)"
    msg = "Safe Surplus. Excellent viability."
elif runway_weeks >= weeks_remaining:
    status = "VIABLE (ON TRACK)"
    color = "#22c55e" # Green
    bg = "rgba(34, 197, 94, 0.1)"
    msg = "Fully funded for remaining time."
elif runway_weeks >= max(0, weeks_remaining - 2):
    status = "TIGHT (MONITOR)"
    color = "#eab308" # Yellow
    bg = "rgba(234, 179, 8, 0.1)"
    msg = "Tight budget. Watch billing closely."
else:
    status = "NON-VIABLE"
    color = "#ef4444" # Red
    bg = "rgba(239, 68, 68, 0.1)"
    msg = "Insufficient funds. Action required."

# ==============================================================================
# MAIN DASHBOARD
# ==============================================================================

# 1. STATUS BANNER
st.markdown(f"""
    <div class="status-banner" style="border-color: {color}; background-color: {bg};">
        <h1 style="color: {color}; margin:0;">{status}</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.8;">{msg}</p>
        <div style="margin-top: 10px; font-weight: bold; color: {color};">
            Runway: {runway_weeks:.1f} wks <span style="color: #666;">vs</span> Plan: {weeks_remaining:.1f} wks
        </div>
    </div>
""", unsafe_allow_html=True)

# 2. METRICS
m1, m2, m3, m4 = st.columns(4)
m1.metric("💰 Current Balance", f"${current_balance:,.2f}", "Portal Truth")
m2.metric("💸 Weekly Burn", f"${weekly_cost:,.2f}", f"{hours_per_week}h @ ${hourly_rate:.0f}")
m3.metric("📅 Depletion Date", depletion_date.strftime("%d/%m/%Y"), f"{buffer_weeks:+.1f} wks buffer")
m4.metric("🏁 End Result", f"${surplus_shortfall:,.2f}", "Surplus" if surplus_shortfall > 0 else "Shortfall", 
          delta_color="normal" if surplus_shortfall < 0 else "inverse")

# 3. CHARTS
st.subheader("📊 Financial Trajectory")
tab1, tab2 = st.tabs(["Burn-Down", "Budget Pie"])

with tab1:
    chart_weeks = int(weeks_remaining) + 5
    dates = [today + timedelta(weeks=w) for w in range(chart_weeks)]
    
    # Logic for lines
    y_actual = [max(0, current_balance - (w * weekly_cost)) for w in range(chart_weeks)]
    
    # Create DF
    df_chart = pd.DataFrame({"Date": dates, "Balance": y_actual, "Type": "Your Trajectory"})
    
    fig = px.line(df_chart, x="Date", y="Balance", color="Type", 
                  color_discrete_map={"Your Trajectory": color})
    
    # Add Plan End Line
    fig.add_vline(x=datetime.datetime.combine(plan_end, datetime.time.min).timestamp() * 1000, 
                  line_dash="dot", line_color="white", annotation_text="Plan End")
    
    fig.update_layout(height=350, hovermode="x unified", margin=dict(t=20, b=0, l=0, r=0))
    fig.update_xaxes(tickformat="%d/%m/%Y")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    c1, c2 = st.columns([1, 2])
    with c1:
        spent = max(0, total_budget - current_balance)
        fig_pie = px.pie(values=[spent, current_balance], names=["Used", "Available"], 
                         color_discrete_sequence=["#333333", color], hole=0.5)
        fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=250)
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        st.markdown(f"#### Budget Health")
        st.progress(min((spent/total_budget), 1.0))
        st.caption(f"You have used **{(spent/total_budget)*100:.1f}%** of the original allocation.")

# 4. AI REPORT
st.markdown("---")
col_ai_1, col_ai_2 = st.columns([3, 1])
with col_ai_1:
    st.subheader("🤖 Professional AI Assessment")
with col_ai_2:
    generate_btn = st.button("Generate Report ✨", type="primary", use_container_width=True)

if generate_btn:
    with st.spinner("Analyzing financials and generating strategy..."):
        # Context payload
        ctx = {
            "status": status,
            "weeks_remaining": weeks_remaining,
            "balance": current_balance,
            "weekly_cost": weekly_cost,
            "surplus_shortfall": surplus_shortfall
        }
        report = get_ai_analysis(api_key, ctx)
        
        st.success("Report Generated Successfully")
        st.markdown(f"""
        <div style="background-color: #1e2129; padding: 20px; border-radius: 10px; border-left: 5px solid {color};">
            {report}
        </div>
        """, unsafe_allow_html=True)
elif not api_key:
    st.info("💡 Add a Google Gemini API Key in the sidebar (or secrets) to enable AI reporting.")


# FOOTER
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        © 2025 Xyston Pty Ltd | NDIS Viability Master<br>
        Built by Chas Walker
    </div>
""", unsafe_allow_html=True)
