import pandas as pd
import numpy as np

# Function to calculate mortgage details
def calculate_mortgage(loan_amount, interest_rate, loan_term_years, payment_frequency, start_date, home_price=None, down_payment=None):
    # Determine number of payments based on frequency
    if payment_frequency == "Monthly":
        periods_per_year = 12
    elif payment_frequency == "Bi-weekly":
        periods_per_year = 26
    else:  # Weekly
        periods_per_year = 52
    
    total_periods = loan_term_years * periods_per_year
    
    # Convert annual interest rate to per-period rate
    period_interest_rate = interest_rate / 100 / periods_per_year
    
    # Calculate payment amount using the formula: PMT = PV * r * (1+r)^n / ((1+r)^n - 1)
    if period_interest_rate > 0:
        payment_amount = loan_amount * period_interest_rate * (1 + period_interest_rate) ** total_periods / ((1 + period_interest_rate) ** total_periods - 1)
    else:
        payment_amount = loan_amount / total_periods
    
    # Create amortization schedule
    remaining_balance = loan_amount
    schedule_data = []
    
    for period in range(1, total_periods + 1):
        interest_payment = remaining_balance * period_interest_rate
        principal_payment = payment_amount - interest_payment
        remaining_balance -= principal_payment
        
        # Handle potential negative balances due to rounding in final payment
        if remaining_balance < 0:
            principal_payment += remaining_balance
            payment_amount = principal_payment + interest_payment
            remaining_balance = 0
        
        # Calculate date for this payment
        if payment_frequency == "Monthly":
            payment_date = pd.Timestamp(start_date) + pd.DateOffset(months=period-1)
        elif payment_frequency == "Bi-weekly":
            payment_date = pd.Timestamp(start_date) + pd.DateOffset(days=14*(period-1))
        else:  # Weekly
            payment_date = pd.Timestamp(start_date) + pd.DateOffset(days=7*(period-1))
        
        schedule_data.append({
            "Payment Number": period,
            "Payment Date": payment_date.strftime("%Y-%m-%d"),
            "Payment Amount": payment_amount,
            "Principal Payment": principal_payment,
            "Interest Payment": interest_payment,
            "Remaining Balance": remaining_balance
        })
    
    # Create DataFrame from the schedule data
    schedule_df = pd.DataFrame(schedule_data)
    
    # Calculate total payments and interest
    total_payments = payment_amount * total_periods
    total_interest = total_payments - loan_amount
    
    return {
        "payment_amount": payment_amount,
        "total_payments": total_payments,
        "total_interest": total_interest,
        "schedule_df": schedule_df,
        "loan_amount": loan_amount,
        "interest_rate": interest_rate,
        "loan_term_years": loan_term_years,
        "payment_frequency": payment_frequency,
        "home_price": home_price,
        "down_payment": down_payment,
        "down_payment_percent": None if home_price is None or home_price == 0 else (down_payment / home_price) * 100
    }

def project_income(monthly_income, annual_growth_rate, years):
    """
    Projects future income based on a growth rate.
    :param income: Current income
    :param growth_rate: Annual growth rate (as a decimal)
    :param year: Number of years to project
    :return: Projected monthly income over the specified years as dataframe    
    """
    # Calculate projected income for each year

    months = years * 12
    income_data = []

    for month in range(months):
        year = month // 12
        adjusted_income = monthly_income * ((1 + annual_growth_rate / 100) ** year)
        income_data.append(adjusted_income)

    df = pd.DataFrame({
        "Month": pd.date_range(start=pd.Timestamp.today(), periods=months, freq='ME'),
        "Income": income_data
    })

    df['Month'] = df['Month'].dt.strftime('%Y-%m')

    return df


# print(project_income(180000, 3, 10))