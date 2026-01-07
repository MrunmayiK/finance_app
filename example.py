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
    revenue = st.number_input("Annual Revenue",min_value=0.0, value = 1_000_000.0) 
    num_lines = st.selectbox("Number of Production Lines", [1,2,3,4,5,6,7,8,9,10], index=0)
    analysis_years = st.selectbox("Analysis Period (Years)", [3, 5, 7, 10], index=1)
    discount_rate = st.slider("Discount Rate (%)", 5, 20, 10) / 100

    st.header("IIoT Cost")
    iiot_cost = st.number_input("IIoT License Cost", min_value=0.0, value=50_000.0)
    imp_cost = st.number_input("Implementation Cost", min_value=0.0, value=25_000.0)
   # prod_inc_per = st.number_input("Production Increase (%)", min_value=0.0, value=15.0)

    num_increments = st.selectbox("Production Increase", [1,2,3,4,5], index=0)
    cols = st.columns(num_increments)
    incremental_pcts = []

    for i, col in enumerate(cols):
        with col:
            pct = st.number_input(
            f"(%)",min_value=-100.0,max_value=100.0,value=0.0,step=0.5,format="%.2f", key=f"prod_inc_{i}")
            incremental_pcts.append(pct)

    annual_iiot_cost = st.number_input("License fee/Annual cost",min_value=0.0,value=10000.00)

    

# --------------------------------------------------
# TABS STRUCTURE
# --------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "Metrics Selection",
    "Financial Inputs",
    "Investment Analysis"
])

#AVAILABLE_METRICS = {
#    "Production Volume": {
#        "key": "production",
#        "inputs": ["prod_unit"],
#        "label": "Production Units"
#    },
#    "Average Cost": {
#        "key": "avg_cost",
#        "inputs": ["avg_unit_cost"],
#        "label": "Average Cost per Unit"
#    },
#    "Average Price": {
#        "key": "avg_price",
#        "inputs": ["avg_unit_price"],
#        "label": "Average Price per Unit"
#    },
#    "Downtime Reduction": {
#        "key": "downtime",
#        "inputs": ["downtime_pct"],
#        "label": "Downtime Reduction (%)"
#    },
#    "Maintenance Cost": {
#        "key": "maintenance",
#        "inputs": ["maintenance_cost"],
#        "label": "Maintenance Cost (%)"
#    },
#    "Labor Cost": {
#        "key": "labor",
#        "inputs": ["labor_cost"],
#        "label": "Labor Cost (%)"
#    }
#}


# ==================================================
# TAB 1 : METRICS SELECTION
# ==================================================

with tab1:
    st.header("Metrics Selection")
   # selected_metrics = st.multiselect(
    #    "Choose the metrics you want to model",
    #    options=list(AVAILABLE_METRICS.keys()),
       # default=["Production Volume", "Average Cost", "Average Price"]
   # )

    production_selected = st.checkbox("Production Volume")
    avg_cost_selected = st.checkbox("Average Cost")
    avg_price_selected = st.checkbox("Average Price")
    downtime_selected = st.checkbox("Downtime Reduction")
    maintenance_selected = st.checkbox("Maintenance Cost")
    labor_selected = st.checkbox("Labor Cost")

    selected_metrics = []

    if production_selected:
        selected_metrics.append("Production Volume")
    if avg_cost_selected:
        selected_metrics.append("Average Cost")
    if avg_price_selected:
        selected_metrics.append("Average Price")
    if downtime_selected:
        selected_metrics.append("Downtime Reduction")
    if maintenance_selected:
        selected_metrics.append("Maintenance Cost")
    if labor_selected:
        selected_metrics.append("Labor Cost")

    st.session_state["selected_metrics"] = selected_metrics
 
  
# ==================================================
# TAB 2 : FINANCIAL INPUTS
# ==================================================

selected = st.session_state.get("selected_metrics", [])

with tab2:
    st.header("Financial Inputs")
    
    avg_unit_price = []
    avg_unit_cost = []
    prod_unit = [] 
    downtime_before = 0
    maintenance_before = 0
    labor_before = 0
    downtime_new = 0
    maintenance_pct = 0
    labor_pct = 0

    col1, col2, col3 = st.columns(3)
    
    if "Downtime Reduction" in selected:
       with col1:
         downtime_before = st.number_input(f"Current Downtime (in months)",value=0)
         downtime_new = st.number_input(f"Downtime period after IIOT (in months)", value=0)
    if "Maintenance Cost" in selected:
       with col2:
         maintenance_before = st.number_input(f"Maintenance Cost (in %)")
         maintenance_pct = st.number_input(f"Maintenance cost after IIOT (in %)")
    if "Labor Cost" in selected:
       with col3:
         labor_before = st.number_input(f"Labor Cost (in %)")
         labor_pct = st.number_input(f"Labor cost after IIOT (in %)")

    for i in range(num_lines):
        with st.expander(f"Line {i + 1} Details", expanded=(i == 0)):

          col1, col2, col3 = st.columns(3)
          if "Average Price" in selected:
             with col1:
               price = st.number_input(f"Average Unit Price (Line {i + 1})",min_value=0.0,value=100.0,key=f"avg_unit_price_{i}")
          else:
               price = 0.0
          avg_unit_price.append(price)  
          if "Average Cost" in selected:
             with col2:
               cost = st.number_input(f"Average Unit Cost (Line {i + 1})", min_value=0.0,value=100.0, key=f"avg_unit_cost_{i}")
          else:
               cost = 0.0
          avg_unit_cost.append(cost)  
          if "Production Volume" in selected:
             with col3:
               units = st.number_input(f"Average Production Units (Line {i + 1})", min_value=0,value=100,key=f"prod_unit_{i}") 
          else:
               units = 0
          prod_unit.append(units)  

#=====================================================
# CORE CALUCALTIONS
#=====================================================

value_added_per_line = []
results = []
total_old_profit = 0
#total_new_profit = 0

for i in range(num_lines):
    unit_profit = avg_unit_price[i] - avg_unit_cost[i]

    old_units = prod_unit[i]
    new_units = old_units
    for pct in incremental_pcts:
        new_units *= (1 + pct / 100)
    #new_units = old_units * (1 + prod_inc_per/100)
    incremental_units = new_units - old_units

    old_profit = old_units * unit_profit
    total_old_profit += old_profit
    value_added = incremental_units * unit_profit
    #new_profit = new_units * unit_profit
    #total_new_profit += new_profit

    value_added_per_line.append(value_added)
    
    results.append({
        "Line": f"Line {i + 1}",
        "Unit Profit": unit_profit,
        "Old Units": old_units,
        "New Units": new_units,
        "Incremental Units": incremental_units,
        "Value Added": value_added,
        "Old Profit": old_profit
    })


benefit = []

old_maint = revenue * maintenance_before/100
new_maint = revenue * maintenance_pct/100
save_maint = old_maint - new_maint

old_labor = revenue * labor_before/100
new_labor = revenue * labor_pct/100
save_labor = old_labor - new_labor

total_savings = save_maint + save_labor

benefit.append({"Old Maintenance": old_maint,
                "New Maintenance": new_maint,
                "Maintenance Benefit": save_maint,
                "Old Labor Cost": old_labor,
                "New Labor Cost": new_labor,
                "Labor Cost Benefit": save_labor,
                "Total Savings": total_savings
    })
                

df_value_added = pd.DataFrame(results)
df_savings = pd.DataFrame(benefit)

with tab2:
   st.header("Value Added per Line (After IIoT)")
   st.dataframe(
    df_value_added.style.format({
        "Unit Profit": "{:,.2f}",
        "Old Units": "{:,.0f}",
        "New Units": "{:,.0f}",
        "Incremental Units": "{:,.0f}",
        "Value Added": "{:,.0f}"
    }),
    use_container_width=True
)
 

   st.header("Savings After IIoT")
   st.dataframe(
    df_savings.style.format({
        "Old Maintenance": "{:,.2f}",
        "New Maintenance": "{:,.2f}",
        "Maintenance Benefit": "{:,.2f}",
        "Old Labor Cost": "{:,.2f}",
        "New Labor Cost": "{:,.2f}",
        "Labor Cost Benefit": "{:,.2f}",
        "Total Savings": "{:,.2f}"
    }),
    use_container_width=True
)

total_annual_benefit = sum(value_added_per_line)
net_annual_cashflow = total_annual_benefit - annual_iiot_cost + total_savings
investment_cost = iiot_cost + imp_cost


years = list(range(1, analysis_years + 1))

pv_cashflows = [
    net_annual_cashflow / ((1 + discount_rate) ** y)
    for y in years
]
npv = sum(pv_cashflows) - investment_cost
roi_percent = (sum(pv_cashflows) / investment_cost) * 100 if investment_cost else 0

avg_annual_pv = sum(pv_cashflows) / analysis_years
payback_years = investment_cost / total_annual_benefit if total_annual_benefit > 0 else 0
payback_months = payback_years * 12 if payback_years else 0



#===============================================================
# TAB #: INVESTMENT ANALYSIS AND VISUALIZATION
#===============================================================

with tab3:
   st.header("Investment Analysis")
   k1, k2, k3, k4, k5 = st.columns(5)

   k1.metric("Total Investment",f"{investment_cost:,.0f}")

   k2.metric("Return on Investments",f"{roi_percent:,.0f}%")

   k3.metric("Payback Period",f"{payback_months:,.0f} months")

   k4.metric("Net Present Value",f"{npv:,.0f}")

   k5.metric("Annual Cashflow",f"{net_annual_cashflow:,.0f}")
   

	
   new_total_cost = total_old_profit + total_annual_benefit + total_savings - annual_iiot_cost
 
   fig = go.Figure(go.Waterfall(name="Cost Impact",orientation="v",measure=["absolute", "relative", "relative","relative", "total"],
        x=["Old Profit","Production Increase","Total Savings","Annual IIOT subscription fee","New Profit"],
        y=[total_old_profit, +total_annual_benefit,+total_savings,-annual_iiot_cost,new_total_cost],
        text=[f"{total_old_profit:,.0f}", f"+{total_annual_benefit:,.0f}", f"+{total_savings:,.0f}", f"-{annual_iiot_cost:,.0f}",f"{new_total_cost:,.0f}"],
        textposition="outside",connector=dict(line=dict(color="gray")), increasing=dict(marker=dict(color="#00CC96")),decreasing=dict(marker=dict(color="#EF553B")),totals=dict(marker=dict(color="#636EFA"))))
   fig.update_layout(title="Annual Cost Reduction Breakdown (After IIoT)",yaxis_title="Annual Profit", height=450, margin=dict(t=80, l=60, r=40, b=40),template="plotly_white",showlegend=False)

   fig.update_yaxes(tickformat=",")

   fig

     
