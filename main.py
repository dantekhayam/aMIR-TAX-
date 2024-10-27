import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns

# Load Excel data with validation and cleanup
def load_loan_data(file_path):
    try:
        excel_data = pd.ExcelFile(file_path)
        loan_data = excel_data.parse('Loan Data')
        loan_data.columns = loan_data.iloc[0]
        loan_data = loan_data.drop(0).reset_index(drop=True)
        loan_data = loan_data.dropna(how='all', axis=1)
        loan_data.columns = loan_data.columns.str.strip()
        return loan_data[['Loan ID', 'Loan Amount ($C)', 'Duration', 'Interest ($C)', 
                          'Late Fee & Interest ($C)', 'Total Payment ($C)']]
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Loan Calculator with optimized calculations
class LoanCalculator:
    def __init__(self, loan_amount, interest, late_fee, duration):
        self.loan_amount = loan_amount
        self.interest = interest
        self.late_fee = late_fee
        self.duration = duration

    def total_repayment(self):
        return self.loan_amount + self.interest + self.late_fee

    def calculate_apr(self):
        if self.loan_amount == 0 or self.duration == 0:
            return 0
        daily_interest = self.interest / self.loan_amount
        return (daily_interest * 365 / self.duration) * 100

    def calculate_monthly_payment(self):
        return self.total_repayment() / max((self.duration / 30), 1)

# Visualization helpers
def plot_apr_comparison(apr, loan_id):
    apr_values = [apr, 30, 50, 100]  # Example APR values for comparison
    labels = [loan_id, "Competitor A", "Competitor B", "Industry Average"]
    fig, ax = plt.subplots()
    bars = ax.barh(labels, apr_values)
    ax.set_xlabel('APR (%)')
    ax.set_title('APR Comparison')
    for bar in bars:
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2, f'{bar.get_width():.2f}%', va='center')
    st.pyplot(fig)

def plot_repayment_projection(calculator, duration):
    months = np.arange(1, (duration // 30) + 1)
    monthly_repayment = calculator.calculate_monthly_payment()
    plt.figure()
    plt.plot(months, [monthly_repayment] * len(months), marker='o')
    plt.xlabel('Month')
    plt.ylabel('Monthly Repayment ($C)')
    plt.title('Repayment Projection')
    st.pyplot(plt)

# Streamlit interface
st.title("Payday Loan Dashboard")
st.sidebar.title("Loan Calculator")

uploaded_file = st.sidebar.file_uploader("Upload an Excel file", type=["xlsx"])
if uploaded_file:
    loan_data = load_loan_data(uploaded_file)
    if loan_data is not None:
        loan_ids = loan_data['Loan ID'].unique()
        selected_loan_id = st.sidebar.selectbox("Select Loan ID:", loan_ids)
        selected_loan_data = loan_data[loan_data['Loan ID'] == selected_loan_id].iloc[0]

        # Extract and validate loan parameters
        loan_amount = float(selected_loan_data['Loan Amount ($C)'])
        interest = float(selected_loan_data['Interest ($C)'])
        late_fee = float(selected_loan_data['Late Fee & Interest ($C)']) if pd.notnull(selected_loan_data['Late Fee & Interest ($C)']) else 0.0
        duration = int(selected_loan_data['Duration'])

        calculator = LoanCalculator(loan_amount, interest, late_fee, duration)
        total_repayment = calculator.total_repayment()
        apr = calculator.calculate_apr()
        monthly_payment = calculator.calculate_monthly_payment()

        # Display results
        st.write(f"**Loan Amount:** ${loan_amount:,.2f}")
        st.write(f"**Interest:** ${interest:,.2f}")
        st.write(f"**Late Fee & Interest:** ${late_fee:,.2f}")
        st.write(f"**Duration:** {duration} days")
        st.write(f"**Total Repayment:** ${total_repayment:,.2f}")
        st.write(f"**Effective APR:** {apr:.2f}%")
        st.write(f"**Estimated Monthly Payment:** ${monthly_payment:,.2f}")

        # Visualizations
        st.subheader("APR Comparison")
        plot_apr_comparison(apr, selected_loan_id)

        st.subheader("Loan Repayment Projection")
        plot_repayment_projection(calculator, duration)

        st.subheader("Loan Amount Distribution")
        plt.figure()
        sns.histplot(loan_data['Loan Amount ($C)'].astype(float), kde=True)
        plt.xlabel('Loan Amount ($C)')
        plt.ylabel('Frequency')
        plt.title('Loan Amount Distribution')
        st.pyplot(plt)
else:
    st.write("Please upload an Excel file to proceed.")
