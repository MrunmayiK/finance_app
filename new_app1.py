import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="SAMPRAMA FINANCIAL CALCULATOR",
    layout="wide"
)

st.title("SAMPRAMA FINANCIAL CALCULATOR")

# --------------------------------------------------
# SIDEBAR (GLOBAL SETTINGS ONLY)
# --------------------------------------------------
with st.sidebar:
    st.header("Global Settings")

    analysis_years = st.selectbox(
        "Analysis Period (Years)", [3, 5, 7, 10], index=1
    )

    discount_rate = st.slider(
        "Discount Rate (%)", 5, 20, 10
    ) / 100
    
    annual_iiot_cost = st.number_input("License fee/Annual cost",min_value=0.0,value=10000.00)

# --------------------------------------------------
# TABS STRUCTURE
# --------------------------------------------------
tab1, tab4 = st.tabs([
    "Financial Inputs",
   # "Break-Even & Impact",
   # "Investment Analysis",
    "Investment Analysis"
])

# ==================================================
# TAB 1 : FINANCIAL INPUTS
# ==================================================
with tab1:
    st.header("Financial Inputs")

    col_inputs, col_notes = st.columns([1.3, 1])

    with col_inputs:
        st.subheader("Revenue & Margins")

        annual_turnover = st.number_input("Annual Turnover", min_value=0.0, value=1_000_000.0)
        profit_margin = st.number_input("Profit Margin (%)", min_value=0.0, value=10.0)
        sales_admin_margin = st.number_input("Sales & Admin Margin (%)", min_value=0.0, value=10.0)

        st.subheader("Manufacturing Cost Split")
        mat_margin = st.number_input("Material Cost (%)", min_value=0.0, value=40.0)
        labor_margin = st.number_input("Labor Cost (%)", min_value=0.0, value=20.0)

        st.subheader("Production")
        units_per_year = st.number_input("Production Units / Year", min_value=1.0, value=5000.0)

        st.subheader("Capital & IIoT")
        capital_cost = st.number_input("Capital Cost", min_value=0.0, value=1_000_000.0)
        iiot_cost = st.number_input("IIoT License Cost", min_value=0.0, value=50_000.0)
        imp_cost = st.number_input("Implementation Cost", min_value=0.0, value=25_000.0)
        prod_inc_per = st.number_input("Production Increase (%)", min_value=0.0, value=15.0)

    with col_notes:
        st.info(
            """
            **Model Assumptions**
            
            • Capital cost amortised using straight-line (10 years)  
            • IIoT cost treated as one-time investment (Year 0)  
            • ROI, NPV & Payback based on incremental annual profit  
            • 300 working days assumed per year
            """
        )

# --------------------------------------------------
# CORE CALCULATIONS (SHARED)
# --------------------------------------------------
profit_from_margin = annual_turnover * profit_margin / 100
revenue = annual_turnover - profit_from_margin
sales_admin_cost = revenue * sales_admin_margin / 100
mfg_expense = revenue - sales_admin_cost

mat_cost = mfg_expense * mat_margin / 100
labor_cost = mfg_expense * labor_margin / 100

annual_capital_amort = capital_cost / 10

cost_per_unit = mfg_expense / units_per_year
fixed_per_unit = annual_capital_amort / units_per_year
labor_per_unit = labor_cost / units_per_year

units_after = units_per_year * (1 + prod_inc_per / 100)
fixed_per_unit_after = annual_capital_amort / units_after
labor_per_unit_after = labor_cost / units_after

savings_per_unit = (labor_per_unit + fixed_per_unit) - (labor_per_unit_after + fixed_per_unit_after)

profit_after = profit_from_margin + (units_after * savings_per_unit)
incremental_profit = profit_after - profit_from_margin

total_iiot_investment = iiot_cost + imp_cost

net_annual_benefit = incremental_profit - annual_iiot_cost

years = list(range(0, analysis_years + 1))
cash_flows = [-total_iiot_investment] + [net_annual_benefit] * analysis_years

cumulative_cf = []
running = 0
for cf in cash_flows:
  running += cf
  cumulative_cf.append(running)

payback_year = next((y for y, v in zip(years, cumulative_cf) if v >= 0 and y > 0), None)

npv_vals = []
npv_run = 0
for y, cf in zip(years, cash_flows):
  if y == 0:
     npv_run += cf
  else:
     npv_run += cf / ((1 + discount_rate) ** y)
  npv_vals.append(npv_run)

roi_vals = [(cf / total_iiot_investment) * 100 if total_iiot_investment else 0 for cf in cumulative_cf]
#r1, r2, r3 = st.columns(3)
#r1.metric("ROI (%)", f"{roi_vals[-1]:.1f}%")
#r2.metric("NPV", f"{npv_vals[-1]:,.0f}")
#r3.metric("Payback Period (Years)", payback_year if payback_year else "Not Recovered")


df_yearly = pd.DataFrame({
        "Year": years,
        "Cumulative Cash Flow": cumulative_cf,
        "NPV": npv_vals,
        "ROI (%)": roi_vals
    })

#=====================================================
# TAB 4 : NEW INVESTMENT ANALYSIS (ROI / NPV / PAYBACK)
#=====================================================

with tab4:
     
    st.subheader("Investment Snapshot")

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Total Investment",f"{total_iiot_investment:,.0f}")

    k2.metric("Annual Benefit",f"{net_annual_benefit:,.0f}",delta=f"{(net_annual_benefit / total_iiot_investment)*100:.1f}% ROI")

    k3.metric("Payback Period",f"{payback_year:.0f} years")

    k4.metric("NPV",f"{npv_vals[-1]:,.0f}")


    fig_main = go.Figure()

    fig_main.add_bar(
    x=df_yearly["Year"],
    y=df_yearly["Cumulative Cash Flow"],
    name="Cumulative Cash Flow",
    marker_color="#4CAF50")

    fig_main.add_scatter(
    x=df_yearly["Year"],
    y=df_yearly["NPV"],
    name="NPV",
    line=dict(color="#1f77b4", width=3)
)

    fig_main.add_scatter(
    x=df_yearly["Year"],
    y=df_yearly["ROI (%)"],
    name="ROI (%)",
    yaxis="y2",
    line=dict(color="#ff7f0e", dash="dot")
)

    if payback_year:
        fig_main.add_vline(
        x=payback_year,
        line_dash="dash",
        line_color="red",
        annotation_text="Break-even"
    )

    fig_main.update_layout(
        title="Investment Performance Over Time",
    yaxis=dict(title="Cash Flow / NPV"),
    yaxis2=dict(
        title="ROI (%)",
        overlaying="y",
        side="right"
    ),
        legend=dict(orientation="h", y=-0.25),
    height=500
)

    st.plotly_chart(fig_main, use_container_width=True)

    df_profit_compare = pd.DataFrame({
    "Scenario": ["Before IIoT", "After IIoT"],
    "Profit": [profit_from_margin, profit_after]
})

    fig_profit = px.bar(
    df_profit_compare,
    x="Scenario",
    y="Profit",
    text="Profit",
    title="Profit Impact",
    color="Scenario",
    color_discrete_sequence=["#9ecae1", "#2ca02c"]
)

    fig_profit.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside",
    cliponaxis=False
)

    fig_profit.update_layout(
    height=400,
    showlegend=False
)

    df_prod_compare = pd.DataFrame({
    "Scenario": ["Before IIoT", "After IIoT"],
    "Production Units": [units_per_year, units_after]
})

    fig_prod = px.bar(
    df_prod_compare,
    x="Scenario",
    y="Production Units",
    text="Production Units",
    title="Production Volume Impact",
    color="Scenario",
    color_discrete_sequence=["#c7c7c7", "#1f77b4"]
)

    fig_prod.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside",
    cliponaxis=False
)

    fig_prod.update_layout(
    height=400,
    showlegend=False
)

    df_benefit_cost = pd.DataFrame({
    "Category": ["Annual Benefit", "Annual Cost"],
    "Value": [net_annual_benefit, annual_iiot_cost]})

    fig_bc = px.bar(
    df_benefit_cost,
    x="Category",
    y="Value",
    title="Annual Benefit vs Annual Cost",
    text="Value")

    fig_bc.update_traces(texttemplate="%{text:,.0f}", textposition="outside",cliponaxis=False)
    fig_bc.update_layout(
    height=400,
    showlegend=False)
   
    c1, c2, c3 = st.columns(3)

    c1.plotly_chart(fig_profit, use_container_width=True)
    c2.plotly_chart(fig_prod, use_container_width=True)
    c3.plotly_chart(fig_bc, use_container_width=True)

