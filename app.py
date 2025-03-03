import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# Load data
@st.cache_data
def load_data():
    file_path = "CR Sample DB.xlsx"
    df = pd.read_excel(file_path, sheet_name='Sheet1')
    df.columns = df.columns.str.lower()
    return df

df = load_data()

# Page title
st.set_page_config(page_title="Business CR Dashboard", layout="wide", initial_sidebar_state="expanded")
st.title("📊 Business CR Dashboard")
st.markdown("### Monitor and analyze CR data with interactive visualizations")

# Sidebar Filters
st.sidebar.subheader("🎯 Filters")
sector_filter = st.sidebar.multiselect("Sector", df['cr sector english'].dropna().unique().tolist(), default=[])
status_filter = st.sidebar.multiselect("CR Status", df['cr english status'].unique().tolist(), default=[])
municipality_filter = st.sidebar.multiselect("Municipality", df['mun english'].dropna().unique().tolist(), default=[])
company_type_filter = st.sidebar.multiselect("Company Type", df['company type english'].dropna().unique().tolist(), default=[])
cr_activity_filter = st.sidebar.multiselect("CR Activity", df['cr activity english'].dropna().unique().tolist(), default=[])

registration_range = st.sidebar.slider("📅 Registration Year Range", int(df['registration date'].dt.year.min()), int(df['registration date'].dt.year.max()),
                                        (int(df['registration date'].dt.year.min()), int(df['registration date'].dt.year.max())))

expiry_range = st.sidebar.slider("📅 Expiry Year Range", int(df['expiry date'].dt.year.min()), int(df['expiry date'].dt.year.max()),
                                  (int(df['expiry date'].dt.year.min()), int(df['expiry date'].dt.year.max())))

# Apply Filters
filtered_df = df.copy()
if sector_filter:
    filtered_df = filtered_df[filtered_df['cr sector english'].isin(sector_filter)]
if status_filter:
    filtered_df = filtered_df[filtered_df['cr english status'].isin(status_filter)]
if municipality_filter:
    filtered_df = filtered_df[filtered_df['mun english'].isin(municipality_filter)]
if company_type_filter:
    filtered_df = filtered_df[filtered_df['company type english'].isin(company_type_filter)]
if cr_activity_filter:
    filtered_df = filtered_df[filtered_df['cr activity english'].isin(cr_activity_filter)]
filtered_df = filtered_df[(filtered_df['registration date'].dt.year >= registration_range[0]) &
                          (filtered_df['registration date'].dt.year <= registration_range[1]) &
                          (filtered_df['expiry date'].dt.year >= expiry_range[0]) &
                          (filtered_df['expiry date'].dt.year <= expiry_range[1])]

# Summary Metrics
st.markdown("---")
st.subheader("📈 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total CRs", len(df))
col2.metric("Active CRs", df[df['cr english status'] == "ACTIVE"].shape[0])
col3.metric("Deleted By Law CRs", df[df['cr english status'] == "DELETED BY LAW"].shape[0])
col4.metric("Total ICR", df[df['company type english'] == "Individual Establishment"].shape[0])
col5.metric("Total CCR", df[df['company type english'] != "Individual Establishment"].shape[0])

# Visuals
st.markdown("---")
st.subheader("📊 Visual Insights")
col1, col2 = st.columns(2)

sector_counts = filtered_df['cr sector english'].value_counts().reset_index()
sector_counts.columns = ['CR Sector English', 'Count']
fig_sector = px.treemap(sector_counts, path=["CR Sector English"], values="Count", title="CR Distribution by Sector")
col1.plotly_chart(fig_sector, use_container_width=True)

fig_status = px.pie(filtered_df, names='cr english status', title='CR Status Distribution', color_discrete_sequence=px.colors.qualitative.Set2)
col2.plotly_chart(fig_status, use_container_width=True)

st.subheader("📍 CRs by Municipality")
fig_municipality = px.bar(filtered_df.groupby("mun english").size().reset_index(name='count'),
                          x='mun english', y='count', title='CRs by Municipality', text_auto=True, color_discrete_sequence=['#EF553B'])
st.plotly_chart(fig_municipality, use_container_width=True)

st.subheader("📅 Yearly Registration Trends")
filtered_df['registration year'] = filtered_df['registration date'].dt.year
fig_yearly = px.line(filtered_df.groupby("registration year").size().reset_index(name='count'),
                     x='registration year', y='count', title='Registrations Over Time', markers=True, color_discrete_sequence=['#00CC96'])
st.plotly_chart(fig_yearly, use_container_width=True)

# Activity & Industry Analysis
st.markdown("---")
st.subheader("📊 Activity & Industry Analysis")

# Sectoral Growth Over Time
sector_growth = filtered_df.groupby(['registration year', 'cr sector english']).size().reset_index(name='count')
fig_sector_growth = px.line(sector_growth, x='registration year', y='count', color='cr sector english', title='Sectoral Growth Over Time')
st.plotly_chart(fig_sector_growth, use_container_width=True)

# Top 10 Sectors
top_sectors = filtered_df['cr sector english'].value_counts().nlargest(10).reset_index()
top_sectors.columns = ['Sector', 'Count']
fig_top_sectors = px.bar(top_sectors, x='Sector', y='Count', title='Top 10 Sectors', text_auto=True)
st.plotly_chart(fig_top_sectors, use_container_width=True)

# ICR vs CCR Trends
df['registration quarter'] = df['registration date'].dt.to_period('Q').astype(str)
icr_vs_ccr_trend = df.groupby(['registration quarter', 'company type english']).size().reset_index(name='count')
fig_icr_ccr_trend = px.line(icr_vs_ccr_trend, x='registration quarter', y='count', color='company type english', title='ICR vs CCR Growth Trends Over Time')
st.plotly_chart(fig_icr_ccr_trend, use_container_width=True)

# Export Graphs
st.markdown("---")
st.subheader("📤 Export Data")
st.download_button("Download Filtered Data", filtered_df.to_csv(index=False), "filtered_data.csv", "text/csv")

st.markdown("---")
st.markdown("💡 *Developed with Streamlit & Plotly for interactive business insights.*")
