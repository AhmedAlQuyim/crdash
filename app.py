import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# Load data
@st.cache_data
def load_data():
    file_path = "CR Sample DB.xlsx"
    df = pd.read_excel(file_path, sheet_name='Sheet1')
    df.columns = df.columns.str.strip().str.lower()  # Normalize column names
    return df

df = load_data()

# Debug: Display available columns
st.write("Available columns:", df.columns.tolist())

# Page title
st.set_page_config(page_title="Business CR Dashboard", layout="wide", initial_sidebar_state="expanded")
st.title("📊 Business CR Dashboard")
st.markdown("### Monitor and analyze CR data with interactive visualizations")

# Sidebar Filters
st.sidebar.subheader("🎯 Filters")
sector_filter = st.sidebar.selectbox("Sector", ["All"] + df['cr sector english'].dropna().unique().tolist())
status_filter = st.sidebar.selectbox("CR Status", ["All"] + df['cr english status'].unique().tolist())
municipality_filter = st.sidebar.selectbox("Municipality", ["All"] + df['mun english'].dropna().unique().tolist())
company_type_filter = st.sidebar.selectbox("Company Type", ["All"] + df['company type english'].dropna().unique().tolist())

registration_start = st.sidebar.date_input("📅 Registration Start", df['registration date'].min())
registration_end = st.sidebar.date_input("📅 Registration End", df['registration date'].max())
expiry_start = st.sidebar.date_input("📅 Expiry Start", df['expiry date'].min())
expiry_end = st.sidebar.date_input("📅 Expiry End", df['expiry date'].max())

# Apply Filters
filtered_df = df.copy()
if sector_filter != "All":
    filtered_df = filtered_df[filtered_df['cr sector english'] == sector_filter]
if status_filter != "All":
    filtered_df = filtered_df[filtered_df['cr english status'] == status_filter]
if municipality_filter != "All":
    filtered_df = filtered_df[filtered_df['mun english'] == municipality_filter]
if company_type_filter != "All":
    filtered_df = filtered_df[filtered_df['company type english'] == company_type_filter]
filtered_df = filtered_df[(filtered_df['registration date'] >= pd.to_datetime(registration_start)) &
                          (filtered_df['registration date'] <= pd.to_datetime(registration_end)) &
                          (filtered_df['expiry date'] >= pd.to_datetime(expiry_start)) &
                          (filtered_df['expiry date'] <= pd.to_datetime(expiry_end))]

# Summary Metrics
st.markdown("---")
st.subheader("📈 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total CRs", len(df))
col2.metric("Active CRs", df[df['cr english status'] == "ACTIVE"].shape[0])
col3.metric("Deleted By Law CRs", df[df['cr english status'] == "DELETED BY LAW"].shape[0])
col4.metric("Total ICR", df[df['company type english'] == "individual establishment"].shape[0])
col5.metric("Total CCR", df[df['company type english'] != "individual establishment"].shape[0])

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
df['registration year'] = df['registration date'].dt.year
fig_yearly = px.line(df.groupby("registration year").size().reset_index(name='count'),
                     x='registration year', y='count', title='Registrations Over Time', markers=True, color_discrete_sequence=['#00CC96'])
st.plotly_chart(fig_yearly, use_container_width=True)

# Activity & Industry Analysis
st.markdown("---")
st.subheader("📊 Activity & Industry Analysis")

if 'cr activity english' in df.columns:
    df['cr activity english'].fillna("Unknown", inplace=True)
    top_activities = df['cr activity english'].value_counts().head(10).reset_index()
    top_activities.columns = ['CR Activity', 'Count']
    fig_activities = px.bar(top_activities, x='CR Activity', y='Count', title='Top 10 CR Activities', text_auto=True, color_discrete_sequence=['#FFA15A'])
    st.plotly_chart(fig_activities, use_container_width=True)
else:
    st.warning("❗ 'CR Activity English' column is missing from the dataset.")

# Search Feature
st.markdown("---")
st.subheader("🔍 Search CRs")
search_query = st.text_input("Search by CR Number or Name")
if search_query:
    search_results = df[(df['cr number'].astype(str).str.contains(search_query, na=False)) |
                        (df['cr english name'].str.contains(search_query, case=False, na=False))]
    st.dataframe(search_results, use_container_width=True)

# Export Feature
st.markdown("---")
st.subheader("📤 Export Data")
st.download_button("Download Filtered Data", filtered_df.to_csv(index=False), "filtered_data.csv", "text/csv")

st.markdown("---")
st.markdown("💡 *Developed with Streamlit & Plotly for interactive business insights.*")
