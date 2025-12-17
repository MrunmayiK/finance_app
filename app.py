import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.title("Samprama ROI Calculator")
st.set_page_config(layout="wide")

# User Inputs

annual_turnover = st.number_input("Annual Turnover", min_value=0.0)

# Profit 
col_input, col_output = st.columns(2)

with col_input:
 profit_margin = st.number_input("Profit Margin (%)", min_value=0.0)

with col_output:
 profit_from_margin = annual_turnover * (profit_margin / 100)
 st.metric("Profit (from margin)",f"{profit_from_margin:,.2f}")
    

# Revenue
revenue = annual_turnover - profit_from_margin
st.metric ("Revenue",f"{revenue:,.2f}")

# Sales and Admin Cost
col_input, col_output = st.columns(2)

with col_input:
 sales_admin_margin = st.number_input("Sales and Admin Margin (%)", min_value=0.0)

with col_output:
 sales_admin_percent = revenue * (sales_admin_margin / 100)
 st.metric("Sales and Admin Cost(from margin)",f"{sales_admin_percent:,.2f}")
    

# Manufactring cost
mfg_expense = revenue - sales_admin_percent
st.metric ("Manufacturing cost",f"{mfg_expense:,.2f}")

# Material Cost
col_input, col_output = st.columns(2)

with col_input:
 mat_margin = st.number_input("Material Margin (%)", min_value=0.0)

with col_output:
 mat_from_margin = mfg_expense * (mat_margin / 100)
 st.metric("Material Cost (from margin)",f"{mat_from_margin:,.2f}")
    

# Labor Cost
col_input, col_output = st.columns(2)

with col_input:
 labor_margin = st.number_input("labor Margin (%)", min_value=0.0)

with col_output:
  labor_from_margin = mfg_expense * (labor_margin / 100)
  st.metric("Labor Cost (from margin)",f"{labor_from_margin:,.2f}")
    

# Capital Cost

capital_cost = st.number_input("Capital Cost", min_value=0.0)


before_col, mid_col, after_col = st.columns(3)

#----------Before IIOT----------
with before_col:
	st.subheader("Before Vsmart")

# Production

	units_per_year = st.number_input("Production units per year", min_value=1.0)

	cost_per_unit = mfg_expense / units_per_year
	st.metric ("Cost per unit",f"{cost_per_unit:,.2f}")

	prod_per_day = units_per_year / 300
	st.metric ("Production per day (assuming 300 working days)", f"{prod_per_day:,.2f}")

	mat_per_unit = mat_from_margin / units_per_year 
	st.metric ("Material cost per piece",f"{mat_per_unit:,.2f}")

	labor_per_unit = labor_from_margin / units_per_year
	st.metric ("Labor cost per piece",f"{labor_per_unit:,.2f}")

	fixed_per_unit = capital_cost*0.1/units_per_year
	st.metric ("Fixed cost per piece",f"{fixed_per_unit:,.2f}")


# IIOT cost

#------------Enters IIoT----------------------
with mid_col:
	st.subheader("VSmart IIoT Solution")
	iiot_cost = st.number_input("Cost of Vsmart IIOT solution license", min_value=0.0)
	imp_cost = st.number_input("Cost of implementation" , min_value=0.0)
	prod_inc_per = st.number_input("Increase in production (in %)", min_value=0.0)

# After IIoT
#-----------------After IIoT------------------

with after_col:
	st.subheader("After VSmart")
	
#Production after results
	units_per_sol = units_per_year + (units_per_year*prod_inc_per /100)
	st.metric("New Production units per year",f"{units_per_sol:,.2f}", delta=f"{units_per_sol - units_per_year:,.0f}")

	cost_per_sol = mfg_expense / units_per_sol
	st.metric("New cost per unit",f"{cost_per_sol:,.2f}", delta=f"{cost_per_sol - cost_per_unit:,.0f}")

	prod_per_sol = units_per_sol / 300
	st.metric("New production per day",f"{prod_per_sol:,.2f}", delta=f"{prod_per_sol - prod_per_day:,.0f}")

	fixed_per_sol = (capital_cost*0.1)/units_per_sol
	st.metric("New fixed cost per piece",f"{fixed_per_sol:,.2f}", delta=f"{fixed_per_sol - fixed_per_unit:,.0f}")

	labor_per_sol = labor_from_margin/units_per_sol
	st.metric("New labor cost",f"{labor_per_sol:,.2f}", delta=f"{labor_per_sol - labor_per_unit:,.0f}")
	
	savings_per_unit = ((labor_per_unit + fixed_per_unit) -(labor_per_sol + fixed_per_sol))
	st.metric("Savings",f"{savings_per_unit:,.2f}")

	overall_profit = profit_from_margin + (units_per_sol * savings_per_unit)
	st.metric("Overall improvement in profit",f"{overall_profit:,.2f}", delta=f"{overall_profit - profit_from_margin:,.0f}" )
	
#-------------------- ROI , payback and NPV --------------------

incremental_profit = overall_profit - profit_from_margin
total_iiot_investment = iiot_cost + imp_cost
#if total_iiot_investment > 0:
#    roi_percent = (incremental_profit / total_iiot_investment) * 100
#else:
#    roi_percent = 0
#st.metric("ROI (%)", f"{roi_percent:,.2f}%")



#if incremental_profit > 0:
#    payback_years = total_iiot_investment / incremental_profit
#else:
#    payback_years = 0
#st.metric("Payback Period (Years)", f"{payback_years:,.2f}")


#analysis_years = st.number_input("Analysis Period (Years)",min_value=1,value=5)
#discount_rate = st.number_input("Discount Rate (%)",min_value=0.0,value=10.0)

#discount_rate_decimal = discount_rate / 100

#npv = -total_iiot_investment

#for year in range(1, analysis_years + 1):
#    npv += incremental_profit / ((1 + discount_rate_decimal) ** year)
#st.metric("Net Present Value (NPV)", f"{npv:,.2f}")
#----------------- Graphs ------------------------------

df = pd.DataFrame({
    "Scenario": ["Before IIoT", "After IIoT"],
    "Profit": [profit_from_margin, overall_profit],
    "Production": [units_per_year, units_per_sol]
})
	
fig = go.Figure()

# Profit (Bar)
fig.add_trace(
    go.Bar(
        x=df["Scenario"],
        y=df["Profit"],
        name="Profit",
        text=df["Profit"],
        texttemplate="%{text:,.0f}",
        textposition="outside",
        yaxis="y1"
    )
)

# Production (Line)
fig.add_trace(
    go.Scatter(
        x=df["Scenario"],
        y=df["Production"],
        name="Production Units",
        mode="lines+markers",
        yaxis="y2"
    )
)

# Layout FIXES
fig.update_layout(
    title="Before vs After IIoT: Profit & Production Impact",
    height=500,
    margin=dict(l=90, r=90, t=80, b=60), 

    xaxis=dict(
        title="Scenario"
    ),

    yaxis=dict(
        title="Profit",
        automargin=True,
        showgrid=True
    ),

    yaxis2=dict(
        title="Production Units",
        overlaying="y",
        side="right",
        automargin=True,
        position=1.0 
    ),

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.25,
        xanchor="center",
        x=0.5
    )
)

st.plotly_chart(fig, use_container_width=True)
# ---------------------------------------------------------------waterfall chart----------------------------------

fig1 = go.Figure(
    go.Waterfall(
        name="Profit Bridge",
        orientation="v",
        measure=["absolute", "relative", "relative", "total"],
        x=[
            "Profit Before IIoT",
            "Production Increase",
            "Cost Reduction",
            "Profit After IIoT"
        ],
        y=[
            profit_from_margin,
            units_per_sol,
            savings_per_unit,
            overall_profit
        ],
        text=[
            f"{profit_from_margin:,.0f}",
            f"+{units_per_sol:,.0f}",
            f"+{savings_per_unit:,.0f}",
            f"{overall_profit:,.0f}"
        ],
        textposition="outside",
        connector={"line": {"width": 1}},
    )
)

fig1.update_layout(
    title="Profit Waterfall: Impact of IIoT Implementation",
    height=500,
    margin=dict(l=80, r=80, t=80, b=60),
    yaxis_title="Profit",
)

st.plotly_chart(fig1, use_container_width=True)

#----------------------------------------------- Over the years graph ---------------------------
analysis_years_options = [3, 5, 7, 10]

analysis_years = st.selectbox("Select Analysis Period (Years)",analysis_years_options,index=1)
discount_rate = st.number_input("Discount Rate (%)",min_value=0.0,value=10.0) / 100

years = list(range(0, analysis_years + 1))
cash_flows = []

for year in years:
    if year == 0:
        cash_flows.append(-total_iiot_investment)
    else:
        cash_flows.append(incremental_profit)

cumulative_cashflow = []
running_total = 0

for cf in cash_flows:
    running_total += cf
    cumulative_cashflow.append(running_total)

payback_year = 0
for year, value in zip(years, cumulative_cashflow):
    if value >= 0 and year != 0:
        payback_year = year
        break

npv_by_year = []
npv_running = 0

for year, cf in zip(years, cash_flows):
    if year == 0:
        npv_running += cf
    else:
        npv_running += cf / ((1 + discount_rate) ** year)
    npv_by_year.append(npv_running)


roi_by_year = []

for cum_cf in cumulative_cashflow:
    if total_iiot_investment > 0:
        roi_by_year.append((cum_cf / total_iiot_investment) * 100)
    else:
        roi_by_year.append(0)

df_yearly = pd.DataFrame({
    "Year": years,
    "Annual Cash Flow": cash_flows,
    "Cumulative Cash Flow": cumulative_cashflow,
    "NPV": npv_by_year,
    "ROI (%)": roi_by_year
})

st.subheader("Year-wise Financial Performance")
st.dataframe(df_yearly)


fig_cf = px.line(
    df_yearly,
    x="Year",
    y="Cumulative Cash Flow",
    title="Cumulative Cash Flow (Payback Analysis)",
    markers=True
)

fig_cf.add_hline(y=0, line_dash="dash")

st.plotly_chart(fig_cf, use_container_width=True)

fig_npv = px.line(
    df_yearly,
    x="Year",
    y="NPV",
    title="NPV Evolution Over Time",
    markers=True
)

fig_npv.add_hline(y=0, line_dash="dash")

st.plotly_chart(fig_npv, use_container_width=True)

fig_roi = px.line(
    df_yearly,
    x="Year",
    y="ROI (%)",
    title="ROI Growth Over Time",
    markers=True
)

st.plotly_chart(fig_roi, use_container_width=True)

#-------------------------------------------------- one graph for all 3 KPis -----------------------------------

df_before = df_yearly[df_yearly["Year"] <= payback_year]
df_after = df_yearly[df_yearly["Year"] >= payback_year]


fig2 = go.Figure()

# ---------- CUMULATIVE CASH FLOW ----------
fig2.add_trace(
    go.Scatter(
        x=df_before["Year"],
        y=df_before["Cumulative Cash Flow"],
        name="Cumulative Cash Flow (Before BE)",
        line=dict(color="red", width=3),
        yaxis="y1"
    )
)

fig2.add_trace(
    go.Scatter(
        x=df_after["Year"],
        y=df_after["Cumulative Cash Flow"],
        name="Cumulative Cash Flow (After BE)",
        line=dict(color="green", width=3),
        yaxis="y1"
    )
)

# ---------- NPV ----------
fig2.add_trace(
    go.Scatter(
        x=df_yearly["Year"],
        y=df_yearly["NPV"],
        name="NPV",
        line=dict(color="blue", dash="dash"),
        yaxis="y1"
    )
)

# ---------- ROI ----------
fig2.add_trace(
    go.Scatter(
        x=df_yearly["Year"],
        y=df_yearly["ROI (%)"],
        name="ROI (%)",
        line=dict(color="orange", dash="dot"),
        yaxis="y2"
    )
)

# ---------- BREAK-EVEN MARKER ----------
fig2.add_vline(
    x=payback_year,
    line_dash="dot",
    line_width=2,
    line_color="black",
    annotation_text=f"Break-even Year {payback_year}",
    annotation_position="top"
)

# ---------- LAYOUT ----------
fig2.update_layout(
    title="IIoT Investment Performance Over Time",
    height=550,
    margin=dict(l=80, r=80, t=80, b=60),

    xaxis=dict(title="Year"),

    yaxis=dict(
        title="Cash Flow / NPV",
        automargin=True
    ),

    yaxis2=dict(
        title="ROI (%)",
        overlaying="y",
        side="right",
        automargin=True
    ),

    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.3,
        xanchor="center",
        x=0.5
    )
)

st.plotly_chart(fig2, use_container_width=True)







#----------------------------------------------------------------------------------------------------
# sales_admin_percent = st.sidebar.number_input("Enter sales and admin percentage",min_value=0)
#mat_percent = st.sidebar.number_input("Enter material cost percentage",min_value=0)
#labor_percent = st.number_input("Enter labor cost percentage",min_value=0)
#capital_cost = st.number_input("Capital Cost", min_value=0.0)
#material_cost = st.number_input("Material Cost", min_value=0.0)
#fixed_cost = st.number_input("Fixed Costs", min_value=0.0)
#investment = st.number_input("Initial Investment", min_value=0.0) 

# Calculations
# profit = profit_percent*annual_turnover/100
#revenue = annual_turnover - profit
#sales_admin_expense = sales_admin_percent*revenue/100
#mfg_expense = revenue - sales_admin_expense
#mat_cost = mat_percent*mfg_expense/100
#labor_cost = labor_percent*mfg_expense/100

#roi = (profit / investment) * 100 if investment != 0 else 0

# Output
#st.subheader("Results")
#st.metric("Annual Revenue", f"{revenue:,.2f}")
#st.metric("Annual Profit", f"{profit:,.2f}")
#st.metric("Sales and Admin Expense", f"{sales_admin_expense:,.2f}")
#st.metric("Manufacturing expense", f"{mfg_expense:,.2f}")
#st.metric("Material Cost", f"{mat_cost:,.2f}")
#st.metric("Labor Cost", f"{labor_cost:,.2f}")
#st.metric("ROI (%)", f"{roi:.2f}")
