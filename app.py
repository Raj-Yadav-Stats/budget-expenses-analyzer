import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.title("Expenses and Budget Analyzer")

# Initialize Session State
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Category", "Amount", "Date"])

# Sidebar for Budget Control
st.sidebar.header("Budget Settings")
budget = st.sidebar.slider("Set Monthly Budget (₹)", min_value=0, max_value=100000, value=5000)

# Add Expense Form
with st.form("expense_form"):
    st.write("Add New Expense")
    category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Books", "Other"])
    amount = st.number_input("Amount (₹)", min_value=0)
    date = st.date_input("Date")
    submit_button = st.form_submit_button("Add Expense")

# Store Expenses
if submit_button and amount > 0:
    new_expense = pd.DataFrame([{"Category": category, "Amount": amount, "Date": date}])
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)
    st.session_state.expenses["Date"] = pd.to_datetime(st.session_state.expenses["Date"])
    st.success("Expense added successfully!")
else:
    st.warning("Amount should be greater than zero.")

# Display Expenses
if not st.session_state.expenses.empty:
    st.write("### Your Expenses")
    st.dataframe(st.session_state.expenses)

    # Save Expenses as CSV
    csv = st.session_state.expenses.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name="expenses.csv", mime="text/csv")

    # Budget Utilization
    total_expenses = st.session_state.expenses["Amount"].sum()
    budget_utilization = (total_expenses / budget) * 100 if budget > 0 else 0
    st.write(f"### Budget Utilization: {budget_utilization:.2f}%")
    st.progress(min(1.0, total_expenses / budget))

    # Budget Status
    if total_expenses > budget:
        st.error("You have exceeded your budget!")
    else:
        st.success(f"You are within your budget. Remaining: ₹{budget - total_expenses}")

    # Spending by Category
    st.write("### Spending by Category")
    category_totals = st.session_state.expenses.groupby("Category")["Amount"].sum()
    fig, ax = plt.subplots()
    ax.pie(category_totals, labels=category_totals.index, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

    # Monthly Expense Trend
    st.write("### Expense Trend Over Time")
    st.session_state.expenses["Month"] = st.session_state.expenses["Date"].dt.to_period("M").astype(str)
    monthly_expenses = st.session_state.expenses.groupby("Month")["Amount"].sum()
    fig, ax = plt.subplots(figsize=(8, 4))
    monthly_expenses.plot(kind="line", marker="o", ax=ax, color="b", linewidth=2)
    ax.set_title("Monthly Expenses Over Time", fontsize=12)
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount (₹)")
    ax.grid(True, linestyle="--", alpha=0.6)
    st.pyplot(fig)

    # Outlier Detection
    st.write("### Outlier Detection (Expenses greater than 1.5 * IQR)")
    Q1 = st.session_state.expenses["Amount"].quantile(0.25)
    Q3 = st.session_state.expenses["Amount"].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = st.session_state.expenses[
        (st.session_state.expenses["Amount"] < lower_bound) | (st.session_state.expenses["Amount"] > upper_bound)]
    fig, ax = plt.subplots()
    ax.boxplot(st.session_state.expenses["Amount"], vert=False)
    ax.set_title("Expense Amount Distribution (Outliers Highlighted)")
    st.pyplot(fig)

    if not outliers.empty:
        st.warning(f"⚠️ {len(outliers)} outliers detected!")
        st.dataframe(outliers)
    else:
        st.success("No outliers detected.")

# Upload Expenses CSV
uploaded_file = st.file_uploader("Upload Expenses CSV", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df["Date"] = pd.to_datetime(df["Date"])
        st.session_state.expenses = df
        st.success("Expenses loaded successfully!")
    except Exception as e:
        st.error(f"Error loading file: {e}")

# Dark Mode Compatibility
st.markdown(
    """
    <style>
    body { background-color: #f4f4f4; color: black; }
    </style>
    """,
    unsafe_allow_html=True
)
