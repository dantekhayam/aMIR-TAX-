import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Load Excel data
def load_loan_data(file_path):
    excel_data = pd.ExcelFile(file_path)
    loan_data = excel_data.parse('Loan Data')  # Load the 'Loan Data' sheet
    # Cleaning column names and selecting relevant columns
    loan_data.columns = loan_data.iloc[0]
    loan_data = loan_data.drop(0)
    loan_data = loan_data.dropna(how='all', axis=1)  # Drop any completely empty columns
    loan_data.columns = loan_data.columns.str.strip()  # Strip whitespace from column names
    return loan_data[['Loan ID', 'Loan Amount ($C)', 'Duration', 'Interest ($C)', 'Late Fee & Interest ($C)', 'Total Payment ($C)']]

# Loan Calculator class
class LoanCalculator:
    """Calculator for payday loan metrics."""
    
    def __init__(self, loan_amount, interest, late_fee, duration):
        self.loan_amount = loan_amount
        self.interest = interest
        self.late_fee = late_fee
        self.duration = duration

    def total_repayment(self):
        """Calculate the total repayment required."""
        return self.loan_amount + self.interest + self.late_fee

    def calculate_apr(self):
        """Calculate the Annual Percentage Rate (APR) based on loan duration."""
        daily_interest = self.interest / self.loan_amount
        apr = (daily_interest * 365 / self.duration) * 100  # Convert to annual rate
        return apr

    def calculate_monthly_payment(self):
        """Estimate monthly payments assuming a simple interest model."""
        total_payment = self.total_repayment()
        monthly_payment = total_payment / (self.duration / 30)
        return monthly_payment

# Streamlit interface
st.title("Payday Loan Dashboard")
st.sidebar.title("Loan Calculator")
st.write("This calculator uses data from the TaxCash Dashboard to calculate repayment amounts and APR for payday loans.")

# Load the loan data from the uploaded Excel file
uploaded_file = st.sidebar.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file:
    loan_data = load_loan_data(uploaded_file)

    # Loan ID selection
    loan_ids = loan_data['Loan ID'].unique()
    selected_loan_id = st.sidebar.selectbox("Select Loan ID:", loan_ids)

    # Filter data for the selected loan
    selected_loan_data = loan_data[loan_data['Loan ID'] == selected_loan_id].iloc[0]

    # Extract loan parameters
    loan_amount = float(selected_loan_data['Loan Amount ($C)'])
    interest = float(selected_loan_data['Interest ($C)'])
    late_fee = float(selected_loan_data['Late Fee & Interest ($C)']) if pd.notnull(selected_loan_data['Late Fee & Interest ($C)']) else 0.0
    duration = int(selected_loan_data['Duration'])

    # Calculate metrics
    calculator = LoanCalculator(loan_amount, interest, late_fee, duration)
    total_repayment = calculator.total_repayment()
    apr = calculator.calculate_apr()
    monthly_payment = calculator.calculate_monthly_payment()

    # Display results
    st.write(f"**Loan Amount:** ${loan_amount}")
    st.write(f"**Interest:** ${interest}")
    st.write(f"**Late Fee & Interest:** ${late_fee}")
    st.write(f"**Duration:** {duration} days")
    st.write(f"**Total Repayment:** ${total_repayment:.2f}")
    st.write(f"**Effective APR:** {apr:.2f}%")
    st.write(f"**Estimated Monthly Payment:** ${monthly_payment:.2f}")

    # Add a visualization for APR comparison
    st.subheader("APR Comparison")
    apr_values = [apr, 30, 50, 100]  # Example APR values for comparison
    labels = [selected_loan_id, "Competitor A", "Competitor B", "Industry Average"]

    fig, ax = plt.subplots()
    bars = ax.barh(labels, apr_values, color=['blue', 'orange', 'green', 'red'])
    ax.set_xlabel('APR (%)')
    ax.set_title('APR Comparison with Industry')
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2, f'{width:.2f}%', va='center')
    st.pyplot(fig)

    # Add a line plot for interest and repayment over time
    st.subheader("Loan Repayment Projection")
    months = np.arange(1, (duration // 30) + 1)
    monthly_repayments = [calculator.total_repayment() / len(months)] * len(months)
    plt.figure(figsize=(10, 5))
    plt.plot(months, monthly_repayments, marker='o', linestyle='-', color='b', label='Monthly Repayment')
    plt.xlabel('Month')
    plt.ylabel('Amount ($C)')
    plt.title('Monthly Repayment Over Time')
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

    # Add a table for overall loan metrics
    st.subheader("Overall Loan Metrics")
    st.dataframe(loan_data)

    # Summary statistics
    st.sidebar.subheader("Loan Summary Statistics")
    avg_interest = loan_data['Interest ($C)'].astype(float).mean()
    avg_late_fee = loan_data['Late Fee & Interest ($C)'].astype(float).mean()
    avg_total_payment = loan_data['Total Payment ($C)'].astype(float).mean()

    st.sidebar.write(f"**Average Interest:** ${avg_interest:.2f}")
    st.sidebar.write(f"**Average Late Fee:** ${avg_late_fee:.2f}")
    st.sidebar.write(f"**Average Total Payment:** ${avg_total_payment:.2f}")

    # Display loan distribution by loan amount
    st.subheader("Loan Amount Distribution")
    plt.figure(figsize=(10, 6))
    sns.histplot(loan_data['Loan Amount ($C)'].astype(float), kde=True, color='skyblue')
    plt.xlabel('Loan Amount ($C)')
    plt.ylabel('Frequency')
    plt.title('Distribution of Loan Amounts')
    st.pyplot(plt)

else:
    st.write("Please upload an Excel file to proceed.")
