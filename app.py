from datetime import date, datetime
from collections import defaultdict
import streamlit as st
import csv
import io

from database import (
    create_table,
    add_subscription,
    get_subscriptions,
    cancel_subscription,
    update_subscription,
    rename_subscription
)


    

# ---------- Helper Functions ----------

def days_until(payment_date):
    payment_date = datetime.strptime(payment_date, "%Y-%m-%d").date()
    return (payment_date - date.today()).days

def is_due_soon(payment_date, days=7):
    return days_until(payment_date) <= days

# ---------- App Setup ----------

st.set_page_config(page_title="Subscription Tracker", layout="centered")
create_table()

st.title("Subscription Tracker")
st.caption("Control all your subscriptions from one place.")

# ---------- Add Subscription Form ----------

with st.form("add_subscription"):
    name = st.text_input("Subscription Name")
    amount = st.number_input("Monthly Cost ($)", min_value=0.0, step=1.0)
    billing_cycle = st.selectbox("Billing Cycle", ["Monthly", "Yearly"])
    category = st.selectbox(
        "Category",
        ["Streaming", "Utilities", "SaaS", "Fitness", "Finance", "Other"]
    )
    next_payment = st.date_input("Next Payment Date")

    submitted = st.form_submit_button("Add Subscription")

    if submitted and name:
        add_subscription(
            name,
            amount,
            billing_cycle,
            category,
            str(next_payment)
        )
        st.success("Subscription added")

# ---------- Display Subscriptions ----------

# ---------- Display Subscriptions ----------

st.subheader("Your Subscriptions")

subscriptions = get_subscriptions()

# ---------- Monthly Summary KPIs ----------

if subscriptions:
    monthly_costs = []
    next_payments = []

    for name, amount, cycle, category, next_payment in subscriptions:
        monthly = amount if cycle == "Monthly" else amount / 12
        monthly_costs.append(monthly)
        next_payments.append(days_until(next_payment))

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Subscriptions", len(subscriptions))
    col2.metric("Avg Monthly Cost", f"${sum(monthly_costs)/len(monthly_costs):.2f}")
    col3.metric("Highest Subscription", f"${max(monthly_costs):.2f}")
    col4.metric(
        "Next Payment",
        f"{min(next_payments)} days"
    )


if subscriptions:
    total_monthly = 0.0
    category_totals = defaultdict(float)

    # ---------- CSV Export ----------
    st.subheader("Export")

    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["name", "amount", "billing_cycle", "category", "next_payment"])

    for row in subscriptions:
        writer.writerow(row)

    st.download_button(
        label="Download CSV",
        data=csv_buffer.getvalue(),
        file_name="subscriptions.csv",
        mime="text/csv"
    )

    st.caption("Export your subscriptions to Excel, Google Sheets, or any spreadsheet tool.")

    # ---------- Upcoming Payments ----------
    st.subheader("Upcoming Payments (Next 7 Days)")

    upcoming = []

    for name, amount, cycle, category, next_payment in subscriptions:
        days_left = days_until(next_payment)
        if 0 <= days_left <= 7:
            upcoming.append((days_left, name, amount, cycle, category))

    if upcoming:
        upcoming.sort(key=lambda x: x[0])
        for days_left, name, amount, cycle, category in upcoming:
            st.warning(
                f"{name} • ${amount:.2f} ({cycle}) • {category} • due in {days_left} days"
            )
    else:
        st.write("No payments due in the next 7 days.")

    # ---------- Subscription Cards ----------
    for name, amount, cycle, category, next_payment in subscriptions:

        monthly_cost = amount if cycle == "Monthly" else amount / 12
        total_monthly += monthly_cost
        category_totals[category] += monthly_cost

        days_left = days_until(next_payment)

        with st.container():
            st.markdown("---")
            st.write(f"**{name}**")
            st.write(f"Cost: ${amount:.2f} ({cycle})")
            st.write(f"Category: {category}")

            if is_due_soon(next_payment):
                st.error(f"Payment due in {days_left} days")
            else:
                st.write(f"Next payment in {days_left} days")

            if st.button("❌ Delete", key=f"delete_{name}"):
                cancel_subscription(name)
                st.rerun()

    st.metric("Total Monthly Spend", f"${total_monthly:.2f}")

    st.subheader("Monthly Spend by Category")
    st.bar_chart(category_totals)

else:
    st.info("No subscriptions added yet.")
