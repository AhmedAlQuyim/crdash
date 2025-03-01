import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    file_path = "CR Sample DB.xlsx"
    df = pd.read_excel(file_path, sheet_name='Sheet1')
    return df

df = load_data()

# Page title
st.title("Business CR Dashboard")

# Summary Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total CRs", len(df))
col2.metric("Active CRs", df[df['CR English Status'] == "ACTIVE"].shape[0])
col3.metric("Average CR Age", round((pd.to_datetime("today") - df['Registration Date']).dt.days.mean() / 365, 1))

# Filters
sector_filter = st.selectbox("Filter by Sector", ["All"] + df['CR Sector English'].dropna().unique().tolist())
status_filter = st.selectbox("Filter by CR Status", ["All"] + df['CR English Status'].unique().tolist())
municipality_filter = st.selectbox("Filter by Municipality", ["All"] + df['MUN English'].dropna().unique().tolist())
company_type_filter = st.selectbox("Filter by Company Type", ["All"] + df['Company Type English'].dropna().unique().tolist())

# Date Filters
registration_start = st.date_input("Registration Start Date", df['Registration Date'].min())
registration_end = st.date_input("Registration End Date", df['Registration Date'].max())
expiry_start = st.date_input("Expiry Start Date", df['Expiry Date'].min())
expiry_end = st.date_input("Expiry End Date", df['Expiry Date'].max())

filtered_df = df.copy()
if sector_filter != "All":
    filtered_df = filtered_df[filtered_df['CR Sector English'] == sector_filter]
if status_filter != "All":
    filtered_df = filtered_df[filtered_df['CR English Status'] == status_filter]
if municipality_filter != "All":
    filtered_df = filtered_df[filtered_df['MUN English'] == municipality_filter]
if company_type_filter != "All":
    filtered_df = filtered_df[filtered_df['Company Type English'] == company_type_filter]
filtered_df = filtered_df[(filtered_df['Registration Date'] >= pd.to_datetime(registration_start)) &
                          (filtered_df['Registration Date'] <= pd.to_datetime(registration_end)) &
                          (filtered_df['Expiry Date'] >= pd.to_datetime(expiry_start)) &
                          (filtered_df['Expiry Date'] <= pd.to_datetime(expiry_end))]

# CRs by Sector
fig_sector = px.bar(filtered_df.groupby("CR Sector English").size().reset_index(name='count'),
                    x='CR Sector English', y='count', title='CRs by Sector', text_auto=True)
st.plotly_chart(fig_sector)

# CRs by Status
fig_status = px.pie(filtered_df, names='CR English Status', title='CR Status Distribution')
st.plotly_chart(fig_status)

# CRs by Municipality (Map Visualization)
st.subheader("CRs by Municipality")
fig_municipality = px.bar(filtered_df.groupby("MUN English").size().reset_index(name='count'),
                          x='MUN English', y='count', title='CRs by Municipality', text_auto=True)
st.plotly_chart(fig_municipality)

# Yearly Registration Trends
st.subheader("Yearly Registration Trends")
df['Registration Year'] = df['Registration Date'].dt.year
fig_yearly = px.line(df.groupby("Registration Year").size().reset_index(name='count'),
                     x='Registration Year', y='count', title='Registrations Over Time')
st.plotly_chart(fig_yearly)

# Search Feature
search_query = st.text_input("Search by CR Number or Name")
if search_query:
    search_results = df[(df['CR Number'].astype(str).str.contains(search_query, na=False)) |
                        (df['CR English Name'].str.contains(search_query, case=False, na=False))]
    st.dataframe(search_results)

# Upcoming Expiring CRs
st.subheader("Upcoming Expiring CRs")
st.dataframe(filtered_df[['CR Number', 'CR English Name', 'Expiry Date']].sort_values(by='Expiry Date').head(10))

# Export Feature
st.download_button("Download Filtered Data", filtered_df.to_csv(index=False), "filtered_data.csv", "text/csv")
