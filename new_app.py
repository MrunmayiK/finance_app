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

# --------------------------------------------------
# TABS STRUCTURE
# --------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "Financial Inputs",
    "Break-Even & Impact",
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

# ==================================================
# TAB 2 : BREAK-EVEN & OPERATIONAL IMPACT
# ==================================================
with tab2:
    st.header("Break-Even & Operational Impact")

    k1, k2, k3, k4 = st.columns(4)

    k1.metric("Profit Before", f"{profit_from_margin:,.0f}")
    k2.metric("Profit After", f"{profit_after:,.0f}")
    k3.metric("Incremental Profit", f"{incremental_profit:,.0f}")
    k4.metric("Units After IIoT", f"{units_after:,.0f}")

    df_compare = pd.DataFrame({
        "Scenario": ["Before IIoT", "After IIoT"],
        "Profit": [profit_from_margin, profit_after],
        "Production": [units_per_year, units_after]
    })

    fig_be = go.Figure()

    fig_be.add_bar(
        x=df_compare["Scenario"],
        y=df_compare["Profit"],
        name="Profit"
    )

    fig_be.add_scatter(
        x=df_compare["Scenario"],
        y=df_compare["Production"],
        mode="lines+markers",
        name="Production Units",
        yaxis="y2"
    )

    fig_be.update_layout(
        title="Before vs After IIoT Impact",
        yaxis=dict(title="Profit"),
        yaxis2=dict(title="Production Units", overlaying="y", side="right"),
        legend=dict(orientation="h", y=-0.25),
        height=450
    )

    st.plotly_chart(fig_be, use_container_width=True)

# ==================================================
# TAB 3 : INVESTMENT ANALYSIS (ROI / NPV / PAYBACK)
# ==================================================
with tab3:
    st.header("Investment Analysis")

    years = list(range(0, analysis_years + 1))
    cash_flows = [-total_iiot_investment] + [incremental_profit] * analysis_years

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

    r1, r2, r3 = st.columns(3)
    r1.metric("ROI (%)", f"{roi_vals[-1]:.1f}%")
    r2.metric("NPV", f"{npv_vals[-1]:,.0f}")
    r3.metric("Payback Period (Years)", payback_year if payback_year else "Not Recovered")

    df_yearly = pd.DataFrame({
        "Year": years,
        "Cumulative Cash Flow": cumulative_cf,
        "NPV": npv_vals,
        "ROI (%)": roi_vals
    })

    fig_all = go.Figure()

    fig_all.add_scatter(
        x=df_yearly["Year"],
        y=df_yearly["Cumulative Cash Flow"],
        name="Cumulative Cash Flow",
        line=dict(color="green")
    )

    fig_all.add_scatter(
        x=df_yearly["Year"],
        y=df_yearly["NPV"],
        name="NPV",
        line=dict(color="blue", dash="dash")
    )

    fig_all.add_scatter(
        x=df_yearly["Year"],
        y=df_yearly["ROI (%)"],
        name="ROI (%)",
        yaxis="y2",
        line=dict(color="orange", dash="dot")
    )

    if payback_year:
        fig_all.add_vline(x=payback_year, line_dash="dot")

    fig_all.update_layout(
        title="Multi-Year IIoT Investment Performance",
        yaxis=dict(title="Cash Flow / NPV"),
        yaxis2=dict(title="ROI (%)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=-0.3),
        height=500
    )

    st.plotly_chart(fig_all, use_container_width=True)
