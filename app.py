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
st.set_page_config(page_title="Business CR Dashboard", layout="wide")
st.title("📊 Business CR Dashboard")
st.markdown("### Monitor and analyze CR data with interactive visualizations")

# Summary Metrics
st.markdown("---")
st.subheader("📈 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total CRs", len(df))
col2.metric("Active CRs", df[df['CR English Status'] == "ACTIVE"].shape[0])
col3.metric("Avg CR Age (Years)", round((pd.to_datetime("today") - df['Registration Date']).dt.days.mean() / 365, 1))

# Filters
st.markdown("---")
st.subheader("🎯 Filters")
col1, col2, col3, col4 = st.columns(4)
sector_filter = col1.selectbox("Sector", ["All"] + df['CR Sector English'].dropna().unique().tolist())
status_filter = col2.selectbox("CR Status", ["All"] + df['CR English Status'].unique().tolist())
municipality_filter = col3.selectbox("Municipality", ["All"] + df['MUN English'].dropna().unique().tolist())
company_type_filter = col4.selectbox("Company Type", ["All"] + df['Company Type English'].dropna().unique().tolist())

col5, col6 = st.columns(2)
registration_start = col5.date_input("📅 Registration Start", df['Registration Date'].min())
registration_end = col6.date_input("📅 Registration End", df['Registration Date'].max())
expiry_start = col5.date_input("📅 Expiry Start", df['Expiry Date'].min())
expiry_end = col6.date_input("📅 Expiry End", df['Expiry Date'].max())

# Apply Filters
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

# Visuals
st.markdown("---")
st.subheader("📊 Visual Insights")
col1, col2 = st.columns(2)
fig_sector = px.bar(filtered_df.groupby("CR Sector English").size().reset_index(name='count'),
                    x='CR Sector English', y='count', title='CRs by Sector', text_auto=True, color_discrete_sequence=['#636EFA'])
col1.plotly_chart(fig_sector, use_container_width=True)

fig_status = px.pie(filtered_df, names='CR English Status', title='CR Status Distribution', color_discrete_sequence=px.colors.qualitative.Set2)
col2.plotly_chart(fig_status, use_container_width=True)

st.subheader("📍 CRs by Municipality")
fig_municipality = px.bar(filtered_df.groupby("MUN English").size().reset_index(name='count'),
                          x='MUN English', y='count', title='CRs by Municipality', text_auto=True, color_discrete_sequence=['#EF553B'])
st.plotly_chart(fig_municipality, use_container_width=True)

st.subheader("📅 Yearly Registration Trends")
df['Registration Year'] = df['Registration Date'].dt.year
fig_yearly = px.line(df.groupby("Registration Year").size().reset_index(name='count'),
                     x='Registration Year', y='count', title='Registrations Over Time', markers=True, color_discrete_sequence=['#00CC96'])
st.plotly_chart(fig_yearly, use_container_width=True)

# Search Feature
st.markdown("---")
st.subheader("🔍 Search CRs")
search_query = st.text_input("Search by CR Number or Name")
if search_query:
    search_results = df[(df['CR Number'].astype(str).str.contains(search_query, na=False)) |
                        (df['CR English Name'].str.contains(search_query, case=False, na=False))]
    st.dataframe(search_results, use_container_width=True)

# Upcoming Expiring CRs
st.markdown("---")
st.subheader("⏳ Upcoming Expiring CRs")
st.dataframe(filtered_df[['CR Number', 'CR English Name', 'Expiry Date']].sort_values(by='Expiry Date').head(10), use_container_width=True)

# Export Feature
st.markdown("---")
st.subheader("📤 Export Data")
st.download_button("Download Filtered Data", filtered_df.to_csv(index=False), "filtered_data.csv", "text/csv")

st.markdown("---")
st.markdown("💡 *Developed with Streamlit & Plotly for interactive business insights.*")
