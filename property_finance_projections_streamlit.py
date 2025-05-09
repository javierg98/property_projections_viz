import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import uuid

from calculations import calculate_mortgage
from calculations import project_income

st.set_page_config(page_title="Mortgage Calculator", layout="wide")

# Title and Description
st.title("Mortgage Calculator")
st.write("Calculate your mortgage payments and view the complete amortization schedule.")
st.write("Want to add, tax projections over life of loan, prepayment assumptions, refinancing planning based on market projections, max prepayment based on income, solver for savings targets, etc")


# Initialize session state for scenario comparison
if 'scenarios' not in st.session_state:
    st.session_state.scenarios = []
    # Add a unique ID to each scenario
    st.session_state.next_id = 1

# Initialize session state for scenario comparison
if 'revenue_stream' not in st.session_state:
    st.session_state.revenue_stream = []
    # Add a unique ID to each scenario
    st.session_state.next_id = 1

# Initialize session state for Page Selection
if 'page' not in st.session_state:
    st.session_state.page = []


# Main content area
def maincontent():
    st.header("Loan Details")

    with st.form("mortgage_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Option to input home price and down payment or direct loan amount
            calc_method = st.radio("Calculation Method", ["Home Price + Down Payment", "Loan Amount Directly"])
            
            if calc_method == "Home Price + Down Payment":
                home_price = st.number_input(
                    "Home Price ($)",
                    min_value=1000,
                    max_value=100000000,
                    value=500000,
                    step=10000,
                    format="%d"
                )
                
                down_payment_type = st.radio("Down Payment Type", ["Percentage", "Amount"])
                
                if down_payment_type == "Percentage":
                    down_payment_percent = st.number_input(
                        "Down Payment (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=20.0,
                        step=1.0,
                        format="%.1f"
                    )
                    down_payment = home_price * (down_payment_percent / 100)
                    st.write(f"Down Payment Amount: ${down_payment:,.2f}")
                else:
                    down_payment = st.number_input(
                        "Down Payment Amount ($)",
                        min_value=0,
                        max_value=int(home_price),
                        value=int(home_price * 0.2),
                        step=5000,
                        format="%d"
                    )
                    down_payment_percent = (down_payment / home_price) * 100 if home_price > 0 else 0
                    st.write(f"Down Payment Percentage: {down_payment_percent:.1f}%")
                
                loan_amount = home_price - down_payment
                st.write(f"Loan Amount: ${loan_amount:,.2f}")
                
            else:  # Loan Amount Directly
                loan_amount = st.number_input(
                    "Loan Amount ($)",
                    min_value=1000,
                    max_value=10000000,
                    value=300000,
                    step=10000,
                    format="%d"
                )
                home_price = None
                down_payment = None
            
            interest_rate = st.number_input(
                "Annual Interest Rate (%)",
                min_value=0.1,
                max_value=30.0,
                value=4.5,
                step=0.1,
                format="%.2f"
            )
        
        with col2:
            loan_term_years = st.number_input(
                "Loan Term (Years)",
                min_value=1,
                max_value=50,
                value=30,
                step=1,
                format="%d"
            )
            
            payment_frequency = st.selectbox(
                "Payment Frequency",
                options=["Monthly", "Bi-weekly", "Weekly"],
                index=0
            )
            
            start_date = st.date_input("Start Date")
            
            # Add a name for the scenario
            scenario_name = st.text_input("Scenario Name", f"Scenario {st.session_state.next_id}")
        
        # Form submission
        submitted = st.form_submit_button("Calculate")
        
        if submitted:
            # Calculate mortgage details
            mortgage_details = calculate_mortgage(
                loan_amount=loan_amount,
                interest_rate=interest_rate,
                loan_term_years=loan_term_years,
                payment_frequency=payment_frequency,
                start_date=start_date,
                home_price=home_price,
                down_payment=down_payment
            )
            
            # Add scenario to session state
            mortgage_details["name"] = scenario_name
            mortgage_details["id"] = st.session_state.next_id
            st.session_state.scenarios.append(mortgage_details)
            st.session_state.next_id += 1
            
            # Display success message
            st.success(f"Scenario '{scenario_name}' has been added for comparison.")

    # Display scenarios for comparison
    if st.session_state.scenarios:
        st.header("Mortgage Scenarios Comparison")
        
        # Create a comparison table
        comparison_data = []
        for scenario in st.session_state.scenarios:
            comparison_data.append({
                "Scenario": scenario["name"],
                "Loan Amount": f"${scenario['loan_amount']:,.2f}",
                "Interest Rate": f"{scenario['interest_rate']}%",
                "Term (Years)": scenario["loan_term_years"],
                "Payment Frequency": scenario["payment_frequency"],
                "Payment Amount": f"${scenario['payment_amount']:,.2f}",
                "Total Payments": f"${scenario['total_payments']:,.2f}",
                "Total Interest": f"${scenario['total_interest']:,.2f}",
                "Down Payment": f"${scenario['down_payment']:,.2f}" if scenario['down_payment'] is not None else "N/A",
                "Down Payment %": f"{scenario['down_payment_percent']:.1f}%" if scenario['down_payment_percent'] is not None else "N/A"
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True)
        
        # Option to remove scenarios
        if st.button("Clear All Scenarios"):
            st.session_state.scenarios = []
            st.session_state.next_id = 1
            st.experimental_rerun()
        
        # Create visualization for comparison
        st.header("Payment Breakdown Comparison")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Bar chart for payment amounts
        scenarios_names = [s["name"] for s in st.session_state.scenarios]
        payment_amounts = [s["payment_amount"] for s in st.session_state.scenarios]
        
        ax.bar(scenarios_names, payment_amounts)
        ax.set_ylabel("Payment Amount ($)")
        ax.set_title("Payment Amount Comparison")
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        st.pyplot(fig)
        
        # Create a second visualization for total interest vs. principal
        st.header("Principal vs. Interest Comparison")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Set up the bar chart
        x = np.arange(len(scenarios_names))
        width = 0.35
        
        # Get the principal and interest values
        principals = [s["loan_amount"] for s in st.session_state.scenarios]
        interests = [s["total_interest"] for s in st.session_state.scenarios]
        
        # Create the bars
        ax.bar(x - width/2, principals, width, label='Principal')
        ax.bar(x + width/2, interests, width, label='Interest')
        
        # Add labels and title
        ax.set_ylabel('Amount ($)')
        ax.set_title('Principal vs. Interest by Scenario')
        ax.set_xticks(x)
        ax.set_xticklabels(scenarios_names)
        ax.legend()
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        st.pyplot(fig)
        
        # Display amortization schedule for selected scenario
        st.header("Amortization Schedule")
        
        # Let user select which scenario to view
        scenario_options = {s["name"]: i for i, s in enumerate(st.session_state.scenarios)}
        selected_scenario_name = st.selectbox("Select Scenario", list(scenario_options.keys()))
        
        # Get the selected scenario
        selected_scenario = st.session_state.scenarios[scenario_options[selected_scenario_name]]
        
        # Format the currency columns for display
        formatted_df = selected_scenario["schedule_df"].copy()
        for col in ["Payment Amount", "Principal Payment", "Interest Payment", "Remaining Balance"]:
            formatted_df[col] = formatted_df[col].map("${:.2f}".format)
        
        st.dataframe(formatted_df, use_container_width=True)
        
        # Allow downloading the amortization schedule as CSV
        csv = selected_scenario["schedule_df"].to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"Download Amortization Schedule for {selected_scenario_name}",
            data=csv,
            file_name=f"mortgage_amortization_{selected_scenario_name}.csv",
            mime="text/csv",
        )

        st.subheader("Tax Considerations")
        st.write("Consider tax implications of mortgage interest deductions and property taxes. Consult a tax advisor for personalized advice.")
    else:
        st.info("Enter loan details and click 'Calculate' to add a mortgage scenario for comparison.")

def income_page():
    st.header("Income/Cash Flow Projections")
    st.write("This page will allow you to project your income and cash flow over time.")
    # Placeholder for income/cash flow projections logic

    # --- Inputs ---
    st.header("Income & Expense Inputs")

        # --- Income Projection Logic ---
    income_forecasts = []


    col1, col2 = st.columns([1,1])
    with col1:
        with st.form("income_form"):
            income_name = st.text_input("Revenue Name", "Monthly Income")
            income = st.number_input("Current Monthly Income ($)", min_value=0, value=5000, step=100)

            growth_option = st.selectbox(
                "Income Growth Type",
                ["Fixed Annual Growth %", "Inflation-Adjusted (2%)", "Manual per Year"]
            )
            if growth_option == "Fixed Annual Growth %":
                growth_rate = st.slider("Annual Growth Rate (%)", 0.0, 10.0, 3.0)

            submitted = st.form_submit_button("Project Income")
        
    
    if submitted:
        # Calculate mortgage details
        income_details = project_income(
            monthly_income=income,
            annual_growth_rate=growth_rate,  # Placeholder for growth rate
            years=10  # Placeholder for years
        )
        
        # Add scenario to session state
        income_details["name"] = income_name
        income_details["id"] = st.session_state.next_id
        st.session_state.revenue_stream.append(income_details)
        st.session_state.next_id += 1
        income_forecasts.append(income_details)
        
        # Display success message
        st.success(f"Scenario '{income_name}' has been added for comparison.")
        
    # with col2:
    #     expenses = st.number_input("Monthly Expenses ($)", min_value=0, value=3000, step=100)


    if len(income_forecasts) > 0:
        df= income_details.copy()

        # --- Visualizations ---
        st.subheader("📉 Monthly Income, Expenses, and Savings")

        st.line_chart(df.set_index("Month")[["Income"]])

        st.subheader("💰 Cumulative Savings Over 10 Years")
        #st.area_chart(df.set_index("Month")[["Cumulative Savings"]])

        # --- Summary Metrics ---
        total_income = df["Income"].sum()
#         total_expenses = df["Expenses"].sum()
#        total_savings = df["Savings"].sum()
#        savings_rate = (total_savings / total_income) * 100 if total_income > 0 else 0

        st.subheader("📌 Summary")
        st.metric("Total Income (10 yrs)", f"${total_income:,.0f}")
#        st.metric("Total Expenses (10 yrs)", f"${total_expenses:,.0f}")
#        st.metric("Total Savings (10 yrs)", f"${total_savings:,.0f}")
#        st.metric("Average Savings Rate", f"{savings_rate:.2f}%")
    else:
        st.info("Enter income details and click 'Project Income' to add a revenue stream for comparison.")

    

def summary_page():
    st.header("Summary Statistics")
    st.write("This page will provide a summary of your mortgage and income projections allowing you to compare different scenarios.")
    # Placeholder for amortization schedule logic
    if st.session_state.scenarios:
        st.subheader("Mortgage Scenarios")
        for scenario in st.session_state.scenarios:
            st.write(f"**Scenario Name:** {scenario['name']}")
            st.write(f"**Loan Amount:** ${scenario['loan_amount']:,.2f}")
            st.write(f"**Interest Rate:** {scenario['interest_rate']}%")
            st.write(f"**Term (Years):** {scenario['loan_term_years']}")
            st.write(f"**Payment Frequency:** {scenario['payment_frequency']}")
            st.write(f"**Payment Amount:** ${scenario['payment_amount']:,.2f}")
            st.write(f"**Total Payments:** ${scenario['total_payments']:,.2f}")
            st.write(f"**Total Interest:** ${scenario['total_interest']:,.2f}")
            st.write("---")
            st.write(f"**Amortization Schedule:**")
            st.dataframe(scenario["schedule_df"].head(), use_container_width=True)
            st.write("---")

    


#================================= 
# SIDEBAR
#=================================
def sidebar_menu():
    st.sidebar.title("Menu")
    st.sidebar.write("Select a page to navigate:")
    if st.sidebar.button('Home'):
                         st.session_state.page = []
    if st.sidebar.button('Income/Cash Flow Projections'):
                         st.session_state.page = ["Income/Cash Flow Projections"]
    if st.sidebar.button('Summary Info'):
                         st.session_state.page = ["Summary Info"]
    
    # if page == "Mortgage Calculator":
    #     st.session_state.page = []
    # elif page == "Income/Cash Flow Projections":
    #     st.session_state.page = ["Income/Cash Flow Projections"]
    # elif page == "Amortization Schedule":
    #     st.session_state.page = ["Amortization Schedule"]

# Run Main Content and initialize everything

sidebar_menu()
if st.session_state.page == []:
    maincontent()
elif st.session_state.page == ["Income/Cash Flow Projections"]:
     income_page()
elif st.session_state.page == ["Summary Info"]:
     summary_page()