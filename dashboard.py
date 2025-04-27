
import streamlit as st
import pandas as pd
import altair as alt

# Set page config
st.set_page_config(page_title="Integrative Claim Tracker", layout="wide")

# Title
st.title("Integrative Claim Tracker")

# Load data from Google Sheets
sheet_url = "https://docs.google.com/spreadsheets/d/19HFwZWdBBBFzxmPJAe0R0GV1mPfUQm7oU8-JX7Tzae0/export?format=csv&id=19HFwZWdBBBFzxmPJAe0R0GV1mPfUQm7oU8-JX7Tzae0"
df = pd.read_csv(sheet_url)

# KPIs
st.markdown("### Key Performance Indicators")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    total_claims = df['Claim ID'].nunique()
    st.metric(label="Total Claims", value=total_claims)

with kpi2:
    paid_claims = df[df['Claim Status'] == 'Paid']['Claim ID'].nunique()
    st.metric(label="Claims Paid", value=paid_claims)

with kpi3:
    total_billed = df['Amount Billed'].sum()
    st.metric(label="Total Billed", value=f"${total_billed:,.2f}")

with kpi4:
    total_paid = df['Amount Paid by Payer'].sum()
    st.metric(label="Total Paid", value=f"${total_paid:,.2f}")

st.markdown("---")

# Pie Chart: Claim Status Breakdown
st.markdown("### Claim Status Breakdown")
status_counts = df['Claim Status'].value_counts().reset_index()
status_counts.columns = ['Claim Status', 'Count']

pie_chart = alt.Chart(status_counts).mark_arc(innerRadius=50).encode(
    theta=alt.Theta(field="Count", type="quantitative"),
    color=alt.Color(field="Claim Status", type="nominal")
)

st.altair_chart(pie_chart, use_container_width=True)

# Bar Chart: Top Denial Reasons
st.markdown("### Top Denial Reasons")
denial_reasons = df[df['Claim Status'] == 'Denied']['Denial Reason'].value_counts().nlargest(10).reset_index()
denial_reasons.columns = ['Denial Reason', 'Count']

bar_chart = alt.Chart(denial_reasons).mark_bar().encode(
    x=alt.X('Count:Q'),
    y=alt.Y('Denial Reason:N', sort='-x'),
    color=alt.value('#D32F2F')
)

st.altair_chart(bar_chart, use_container_width=True)

# Line Chart: Billed vs Paid Over Time
st.markdown("### Financial Trends: Billed vs Paid")

if 'Date of Service' in df.columns:
    df['Date of Service'] = pd.to_datetime(df['Date of Service'], errors='coerce')
    
    trend_data = df.groupby(df['Date of Service'].dt.to_period('M')).agg({
        'Amount Billed': 'sum',
        'Amount Paid by Payer': 'sum'
    }).reset_index()
    trend_data['Date of Service'] = trend_data['Date of Service'].dt.to_timestamp()

    line_chart = alt.Chart(trend_data).mark_line(point=True).encode(
        x=alt.X('Date of Service:T', title='Month'),
        y=alt.Y('Amount Billed:Q', title='Amount ($)'),
        color=alt.value('#1976D2')
    ) + alt.Chart(trend_data).mark_line(point=True).encode(
        x='Date of Service:T',
        y='Amount Paid by Payer:Q',
        color=alt.value('#388E3C')
    )

    st.altair_chart(line_chart, use_container_width=True)
else:
    st.warning("Date of Service column not found or formatted incorrectly.")

st.markdown("---")

# Data Table Viewer
st.markdown("### Claims Data Table")
st.dataframe(df)
