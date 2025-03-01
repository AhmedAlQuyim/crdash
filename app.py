import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# Load data
@st.cache_data
def load_data():
    file_path = "CR Sample DB.xlsx"
    df = pd.read_excel(file_path, sheet_name='Sheet1')
    return df

df = load_data()

# Page title
st.set_page_config(page_title="Business CR Dashboard", layout="wide", initial_sidebar_state="expanded")
st.title("📊 Business CR Dashboard")
st.markdown("### Monitor and analyze CR data with interactive visualizations")

# Sidebar for theme toggle
if st.sidebar.button("🌙 Toggle Dark Mode"):
    st.markdown("<style>body {background-color: #0E1117; color: white;}</style>", unsafe_allow_html=True)

# Sidebar Filters
st.sidebar.subheader("🎯 Filters")
sector_filter = st.sidebar.selectbox("Sector", ["All"] + df['CR Sector English'].dropna().unique().tolist())
status_filter = st.sidebar.selectbox("CR Status", ["All"] + df['CR English Status'].unique().tolist())
municipality_filter = st.sidebar.selectbox("Municipality", ["All"] + df['MUN English'].dropna().unique().tolist())
company_type_filter = st.sidebar.selectbox("Company Type", ["All"] + df['Company Type English'].dropna().unique().tolist())

registration_start = st.sidebar.date_input("📅 Registration Start", df['Registration Date'].min())
registration_end = st.sidebar.date_input("📅 Registration End", df['Registration Date'].max())
expiry_start = st.sidebar.date_input("📅 Expiry Start", df['Expiry Date'].min())
expiry_end = st.sidebar.date_input("📅 Expiry End", df['Expiry Date'].max())

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

# Summary Metrics
st.markdown("---")
st.subheader("📈 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total CRs", len(df))
col2.metric("Active CRs", df[df['CR English Status'] == "ACTIVE"].shape[0])
col3.metric("Deleted By Law CRs", df[df['CR English Status'] == "DELETED BY LAW"].shape[0])
col4.metric("Total ICR", df[df['Company Type English'] == "Individual Establishment"].shape[0])
col5.metric("Total CCR", df[df['Company Type English'] != "Individual Establishment"].shape[0])

# Visuals
st.markdown("---")
st.subheader("📊 Visual Insights")
col1, col2 = st.columns(2)

# Fix: Aggregate data for treemap visualization
sector_counts = filtered_df['CR Sector English'].value_counts().reset_index()
sector_counts.columns = ['CR Sector English', 'Count']
fig_sector = px.treemap(sector_counts, path=["CR Sector English"], values="Count", title="CR Distribution by Sector")
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

# Activity & Industry Analysis
st.markdown("---")
st.subheader("📊 Activity & Industry Analysis")

# Top 10 CR Activities
if 'CR Activiy English' in df.columns:
    top_activities = df['CR Activiy English'].value_counts().head(10).reset_index()
    top_activities.columns = ['CR Activity', 'Count']
    fig_activities = px.bar(top_activities, x='CR Activity', y='Count', title='Top 10 CR Activities', text_auto=True, color_discrete_sequence=['#FFA15A'])
    st.plotly_chart(fig_activities, use_container_width=True)
else:
    st.warning("❗ 'CR Activiy English' column is missing from the dataset.")

# Sectoral Growth Over Time
if 'CR Sector English' in df.columns:
    sector_growth = df.groupby(['Registration Year', 'CR Sector English']).size().reset_index(name='count')
    fig_sector_growth = px.line(sector_growth, x='Registration Year', y='count', color='CR Sector English', title='Sectoral Growth Over Time')
    st.plotly_chart(fig_sector_growth, use_container_width=True)
else:
    st.warning("❗ 'CR Sector English' column is missing from the dataset.")

# Compnay ICR vs CCR
company_type_comparison = pd.DataFrame({
    "Company Type": ["Individual Establishment (ICR)", "All Other Company Types (CCR)"],
    "Count": [df[df['Company Type English'] == "Individual Establishment"].shape[0], df[df['Company Type English'] != "Individual Establishment"].shape[0]]
})
fig_company_comparison = px.bar(company_type_comparison, x="Company Type", y="Count", title="ICR vs CCR Companies", text_auto=True, color_discrete_sequence=['#636EFA'])
st.plotly_chart(fig_company_comparison, use_container_width=True)

# Search Feature
st.markdown("---")
st.subheader("🔍 Search CRs")
search_query = st.text_input("Search by CR Number or Name")
if search_query:
    search_results = df[(df['CR Number'].astype(str).str.contains(search_query, na=False)) |
                        (df['CR English Name'].str.contains(search_query, case=False, na=False))]
    st.dataframe(search_results, use_container_width=True)

# Export Feature
st.markdown("---")
st.subheader("📤 Export Data")
st.download_button("Download Filtered Data", filtered_df.to_csv(index=False), "filtered_data.csv", "text/csv")

st.markdown("---")
st.markdown("💡 *Developed with Streamlit & Plotly for interactive business insights.*")
