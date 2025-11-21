import streamlit as st
import datetime
from datetime import timedelta
import plotly.express as px
import pandas as pd
import pytz
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

# Custom CSS for Pro UI
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .status-banner { padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 25px; border: 1px solid; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
    .metric-card { background-color: #1e2129; padding: 15px; border-radius: 10px; border: 1px solid #2d3342; text-align: center; }
    .metric-label { font-size: 0.8rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: #ffffff; font-family: monospace; }
    .metric-delta { font-size: 0.8rem; margin-top: 5px; }
    .stButton button { border-radius: 8px; font-weight: 600; transition: all 0.2s; }
    h1, h2, h3 { font-family: 'Inter', sans-serif; letter-spacing: -0.5px; }
    
    /* Quick Link Styling */
    .quick-link a { display: block; padding: 6px 10px; margin: 3px 0; background: #1e2129; border: 1px solid #333; border-radius: 6px; color: #ccc; text-decoration: none; font-size: 0.8rem; transition: all 0.2s; }
    .quick-link a:hover { background: #2d3342; border-color: #555; color: #fff; padding-left: 15px; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# UTILITIES
# ==============================================================================
def get_ai_analysis(api_key, ctx):
    """Fetches a professional report from Google Gemini."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""
        Act as a Senior NDIS Support Coordinator (Australia). 
        Write a formal 'File Note: Viability Assessment' for a participant.
        
        DATA:
        - Status: {ctx['status']}
        - Funds: ${ctx['balance']:,.2f} (Portal Truth)
        - Burn: ${ctx['weekly_cost']:,.2f}/wk ({ctx['hours']:.1f} hrs)
        - Plan Ends: {ctx['end_date']} ({ctx['weeks_remaining']:.1f} wks left)
        - Outcome: ${ctx['surplus_shortfall']:,.2f} ({'Surplus' if ctx['surplus_shortfall']>0 else 'Shortfall'})
        
        OUTPUT FORMAT:
        Start with "Re: Financial Viability Assessment".
        Provide an Executive Summary, Risk Analysis, and 3 Imperative Recommendations.
        Tone: Professional, protective, Australian English.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e: return f"Error: {str(e)}"

# Timezone
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
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="font-size: 3.5rem; margin:0; line-height: 1;">🛡️</h1>
            <h2 style="font-weight: 900; letter-spacing: 3px; margin:0; color: #fff;">XYSTON</h2>
            <p style="font-size: 0.7rem; opacity: 0.6; font-family: monospace; letter-spacing: 1px;">NDIS MASTER v2025.9</p>
        </div>
        <div style="height: 1px; background: linear-gradient(90deg, transparent, #333, transparent); margin: 0 0 20px 0;"></div>
    """, unsafe_allow_html=True)

    # API Key
    api_key = st.secrets.get("GEMINI_API_KEY", None)
    if not api_key:
        with st.expander("🔐 AI Settings"):
            api_key = st.text_input("Google API Key", type="password")

    # Inputs
    st.caption("1. SETUP")
    support_type = st.selectbox("Support Level", list(RATES.keys()), label_visibility="collapsed")
    hourly_rate = st.number_input("Rate ($)", value=RATES[support_type], step=0.01)

    st.caption("2. TIMELINE")
    mode = st.radio("Mode", ["Dates", "Weeks"], horizontal=True, label_visibility="collapsed")
    if mode == "Dates":
        plan_end = st.date_input("Plan End", value=today + timedelta(weeks=40), format="DD/MM/YYYY")
        if plan_end <= today: st.stop()
        weeks_remaining = (plan_end - today).days / 7
    else:
        weeks_remaining = st.number_input("Weeks Left", value=40.0, step=0.5)
        plan_end = today + timedelta(days=int(weeks_remaining*7))
    
    st.caption("3. FINANCIALS (PORTAL TRUTH)")
    total_budget = st.number_input("Original ($)", value=18000.0, step=100.0)
    current_balance = st.number_input("Current ($)", value=14500.0, step=50.0)

    st.caption("4. BILLING")
    hours_per_week = st.number_input("Hours/Week", value=1.5, step=0.1)

    st.markdown("---")
    st.markdown('<div style="text-align:center"><a href="https://www.buymeacoffee.com/h0m1ez187" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" style="width:160px;"></a></div>', unsafe_allow_html=True)

    # --- NEW QUICK LINKS SECTION ---
    st.markdown("---")
    st.markdown("### ⚡ Quick Access")
    
    with st.expander("🛠️ Admin & HR", expanded=False):
        st.markdown("""
        <div class="quick-link">
            <a href="https://secure.employmenthero.com/login" target="_blank">Employment Hero HR</a>
            <a href="https://login.xero.com/" target="_blank">Xero Accounting</a>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("🏦 Banking (Big 4)", expanded=False):
        st.markdown("""
        <div class="quick-link">
            <a href="https://www.commbank.com.au/" target="_blank">Commonwealth (CBA)</a>
            <a href="https://www.westpac.com.au/" target="_blank">Westpac</a>
            <a href="https://www.anz.com.au/" target="_blank">ANZ</a>
            <a href="https://www.nab.com.au/" target="_blank">NAB</a>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("🏛️ NDIS Official", expanded=True):
        st.markdown("""
        <div class="quick-link">
            <a href="https://proda.humanservices.gov.au/" target="_blank">🔐 PACE / PRODA Login</a>
            <a href="https://www.ndiscommission.gov.au/" target="_blank">⚖️ NDIS Commission</a>
            <a href="https://www.ndis.gov.au/news" target="_blank">📰 News & Reviews</a>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# LOGIC ENGINE
# ==============================================================================
weekly_cost = hours_per_week * hourly_rate
runway_weeks = current_balance / weekly_cost if weekly_cost > 0 else 999
depletion_date = today + timedelta(days=int(runway_weeks * 7))
required = weekly_cost * weeks_remaining
surplus = current_balance - required
buffer = runway_weeks - weeks_remaining
break_even = current_balance / weeks_remaining / hourly_rate if weeks_remaining > 0 else 0

# Status Logic
if runway_weeks >= weeks_remaining * 1.2:
    status, color, bg, icon = "PLATINUM CLIENT", "#10b981", "rgba(16, 185, 129, 0.1)", "💎"
    msg = "Safe Surplus. Excellent viability."
elif runway_weeks >= weeks_remaining:
    status, color, bg, icon = "VIABLE (ON TRACK)", "#22c55e", "rgba(34, 197, 94, 0.1)", "✅"
    msg = "Fully funded for remaining time."
elif runway_weeks >= max(0, weeks_remaining - 2):
    status, color, bg, icon = "TIGHT (MONITOR)", "#eab308", "rgba(234, 179, 8, 0.1)", "⚠️"
    msg = "Tight budget. Watch closely."
else:
    status, color, bg, icon = "NON-VIABLE", "#ef4444", "rgba(239, 68, 68, 0.1)", "🛑"
    msg = "Insufficient funds. Action required."

# ==============================================================================
# MAIN UI
# ==============================================================================

# 1. STATUS HEADER
st.markdown(f"""
    <div class="status-banner" style="border-color: {color}; background-color: {bg};">
        <h1 style="color: {color}; margin:0; font-size: 2.5rem;">{icon} {status}</h1>
        <p style="color: #ccc; margin-top: 5px;">{msg}</p>
        <div style="margin-top: 15px; font-family: monospace; color: {color};">
            RUNWAY: {runway_weeks:.1f} WKS <span style="color: #555;">|</span> PLAN: {weeks_remaining:.1f} WKS
        </div>
    </div>
""", unsafe_allow_html=True)

# 2. METRIC CARDS
c1, c2, c3, c4 = st.columns(4)
def card(col, label, value, delta, color="#fff"):
    col.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="color: {color};">{value}</div>
            <div class="metric-delta">{delta}</div>
        </div>
    """, unsafe_allow_html=True)

card(c1, "Portal Balance", f"${current_balance:,.0f}", "Real-time Funds", "#fff")
card(c2, "Weekly Burn", f"${weekly_cost:.0f}", f"{hours_per_week}h @ ${hourly_rate:.0f}", "#fff")
card(c3, "Depletion Date", depletion_date.strftime('%d/%m/%y'), f"{buffer:+.1f} wks buffer", color)
card(c4, "End Outcome", f"${surplus:,.0f}", "Surplus" if surplus > 0 else "Shortfall", color)

# 3. THE SANDBOX (Scenario Lab)
st.markdown("### 🧪 Scenario Lab")
with st.expander("Test new billing rates without changing inputs...", expanded=False):
    sim_hours = st.slider("Simulate Hours/Week", 0.0, 5.0, hours_per_week, 0.1)
    sim_cost = sim_hours * hourly_rate
    sim_runway = current_balance / sim_cost if sim_cost > 0 else 999
    sim_surplus = current_balance - (sim_cost * weeks_remaining)
    
    s1, s2, s3 = st.columns(3)
    s1.metric("New Weekly Cost", f"${sim_cost:.2f}", f"{sim_hours} hrs")
    s2.metric("New Runway", f"{sim_runway:.1f} wks", f"{sim_runway - weeks_remaining:+.1f} vs Plan")
    s3.metric("New Outcome", f"${sim_surplus:,.0f}", delta_color="normal" if sim_surplus < 0 else "inverse")

# 4. VISUALS (Ghost Line Chart)
st.markdown("### 📉 Financial Trajectory")
chart_weeks = int(weeks_remaining) + 5
dates = [today + timedelta(weeks=w) for w in range(chart_weeks)]

# Actual Trajectory
y_actual = [max(0, current_balance - (w * weekly_cost)) for w in range(chart_weeks)]
# Ideal Trajectory (Ghost Line)
ideal_burn = current_balance / weeks_remaining if weeks_remaining > 0 else 0
y_ideal = [max(0, current_balance - (w * ideal_burn)) for w in range(chart_weeks)]

df_chart = pd.DataFrame({
    "Date": dates * 2,
    "Balance": y_actual + y_ideal,
    "Scenario": ["Current Trajectory"] * chart_weeks + ["Ideal (Break-Even)"] * chart_weeks
})

fig = px.line(df_chart, x="Date", y="Balance", color="Scenario", 
              color_discrete_map={"Current Trajectory": color, "Ideal (Break-Even)": "#444"})
fig.update_traces(line=dict(width=3))
fig.update_traces(patch={"line": {"dash": "dot"}}, selector={"legendgroup": "Ideal (Break-Even)"})

fig.add_vline(x=datetime.datetime.combine(plan_end, datetime.time.min).timestamp() * 1000, 
              line_dash="dash", line_color="white", annotation_text="Plan End")

fig.update_layout(height=350, hovermode="x unified", margin=dict(t=20, b=0, l=0, r=0), 
                  paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                  legend=dict(orientation="h", y=1.1))
st.plotly_chart(fig, use_container_width=True)

# 5. AI REPORT (API Only)
st.markdown("---")
c_ai1, c_ai2 = st.columns([3,1])
with c_ai1:
    st.markdown("### 🤖 Professional Assessment")
    st.caption("Generates a formal file note for your CRM using Google Gemini.")
with c_ai2:
    if st.button("Generate Note ✨", type="primary", use_container_width=True):
        if api_key:
            with st.spinner("Drafting..."):
                ctx = {"status": status, "balance": current_balance, "weekly_cost": weekly_cost, 
                       "hours": hours_per_week, "end_date": plan_end.strftime('%d/%m/%Y'),
                       "weeks_remaining": weeks_remaining, "surplus_shortfall": surplus}
                report = get_ai_analysis(api_key, ctx)
                st.success("Drafted!")
                st.text_area("Copy to CRM:", value=report, height=300)
        else:
            st.error("Please add your Google API Key in the sidebar to use this feature.")

# FOOTER
st.markdown("---")
st.caption("© 2025 Xyston Pty Ltd | Built by Chas")
