import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import requests

# -------------------------
# Load Data
# -------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("Trip and cases report 2023-2025.xlsx", sheet_name="Trips and Cases")
    df = df.rename(columns={"Country Name": "Country", "International Trips": "Trips"})
    return df

data = load_data()
case_columns = [col for col in data.columns if "Probability" in col]

# -------------------------
# Page Config
# -------------------------
st.set_page_config(page_title="International SOS | Assistance & Travel Risks", layout="wide")

# -------------------------
# Banner with Logo
# -------------------------
st.markdown("""
<style>
.banner-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    background-color: #232762;
    padding: 20px;
}
.banner-title {
    color: white !important;
    margin: 0;
    flex: 1;
    min-width: 250px;
    font-size: 28px;
    order: 1;
    text-align: left;
}
.banner-logo {
    flex: 0;
    min-width: 200px;
    margin-left: 20px;
    order: 2;
}
@media (max-width: 768px) {
    .banner-container {
        flex-direction: column;
        text-align: center;
    }
    .banner-logo {
        order: 0;
        margin: 0 0 15px 0;
    }
    .banner-title {
        order: 1;
        font-size: 22px;
        text-align: center;
        color: white !important;
    }
}
</style>

<div class="banner-container">
    <div class="banner-logo">
        <img src="https://images.learn.internationalsos.com/EloquaImages/clients/InternationalSOS/%7B0769a7db-dae2-4ced-add6-d1a73cb775d5%7D_International_SOS_white_hr_%281%29.png"
             alt="International SOS" style="height:60px; max-width:100%;">
    </div>
    <h1 class="banner-title">
        Assistance and Travel Risks Simulation Report
    </h1>
</div>
""", unsafe_allow_html=True)

st.write("")

# -------------------------
# Intro Section
# -------------------------
st.markdown('<h1 style="color:#232762;">Welcome to the International SOS Travel Risk Simulation Tool</h1>', unsafe_allow_html=True)
st.write("""
This tool provides a simulation of potential medical and security assistance cases based on your traveler volumes.
It uses International SOS proprietary data collected from millions of cases globally.
""")

# -------------------------
# Input Section
# -------------------------
st.markdown('<h2 style="color:#2f4696;">Step 1: Enter Traveler Data</h2>', unsafe_allow_html=True)
st.write("Select countries and input traveler volumes. Add more countries if needed.")

countries, traveler_counts = [], []
country_options = sorted(data["Country"].dropna().unique())

if "num_rows" not in st.session_state:
    st.session_state.num_rows = 3

for i in range(1, st.session_state.num_rows + 1):
    col1, col2 = st.columns([2,1])
    with col1:
        country = st.selectbox(f"Destination Country {i}", [""] + list(country_options), key=f"country{i}")
    with col2:
        travelers = st.number_input(f"Travelers for {country or f'Country {i}'}",
                                    min_value=0, value=0, step=1, key=f"trav{i}")
    if country:
        countries.append(country)
        traveler_counts.append(travelers)

# Place Add/Remove buttons under the last input field
col_add, col_remove = st.columns([1,1])
with col_add:
    if st.button("➕ Add Another Country"):
        st.session_state.num_rows += 1
        st.rerun()
with col_remove:
    if st.session_state.num_rows > 1 and st.button("➖ Remove Last Country"):
        st.session_state.num_rows -= 1
        st.rerun()

# -------------------------
# Results Section
# -------------------------
if countries:
    results = []
    for country, travelers in zip(countries, traveler_counts):
        row = data[data["Country"].str.contains(country, case=False, na=False)]
        if not row.empty:
            case_data, total_cases = {}, 0
            for col in case_columns:
                prob = row.iloc[0][col]
                estimated = travelers * prob
                case_data[col.replace(" Case Probability", "")] = estimated
                total_cases += estimated
            case_data.update({"Country": country, "Travelers": travelers, "Total Cases": total_cases})
            results.append(case_data)
        else:
            results.append({"Country": country, "Travelers": travelers, "Total Cases": 0})

    results_df = pd.DataFrame(results)

    if not results_df.empty:
        total_trips = results_df["Travelers"].sum()
        total_cases = results_df["Total Cases"].sum()

        st.markdown('<h2 style="color:#2f4696;">Step 2: Estimated Assistance Needs</h2>', unsafe_allow_html=True)

        col1, col2 = st.columns([1,2])
        with col1:
            st.metric("Total Travelers", f"{total_trips:,}")
            st.metric("Total Estimated Cases", f"{total_cases:.2f}")
            st.info("""
Probabilities are based on the likelihood of assistance cases **per traveler**, 
with values already converted into decimals (e.g., 0.74% = 0.0074).  
""")
        with col2:
            fig = px.bar(results_df, x="Country", y="Total Cases", 
                        text=results_df["Total Cases"].round(2),
                        color="Country",
                        title="Estimated Cases by Country",
                        color_discrete_sequence=["#2f4696", "#232762", "#4a69bd"])
            st.plotly_chart(fig, use_container_width=True)

        # Toggle between overall and by-country case breakdown
        st.markdown('<h2 style="color:#2f4696;">Case Type Breakdown</h2>', unsafe_allow_html=True)
        view_option = st.radio("View case type breakdown by:", ["Overall", "By Country"], horizontal=True)

        if view_option == "Overall":
            case_totals = results_df.drop(columns=["Country", "Travelers", "Total Cases"]).sum().reset_index()
            case_totals.columns = ["Case Type", "Estimated Cases"]
        else:
            selected_country = st.selectbox("Select a country", results_df["Country"].unique())
            case_totals = results_df[results_df["Country"] == selected_country].drop(
                columns=["Country", "Travelers", "Total Cases"]).T.reset_index()
            case_totals.columns = ["Case Type", "Estimated Cases"]
            case_totals = case_totals[1:]  # remove header row

        fig2 = px.pie(case_totals, values="Estimated Cases", names="Case Type",
                      color_discrete_sequence=["#2f4696", "#009354", "#FFD744", "#DD2484", "#6988C0", "#6C206B", "#EF820F", "#D4002C", "#EEEFEF"])
        fig2.update_layout(legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"))
        st.plotly_chart(fig2, use_container_width=True)

        # Recommendations Section
        st.markdown('<h2 style="color:#2f4696;">What These Results Mean for You</h2>', unsafe_allow_html=True)
        st.write("""
Based on your traveler volumes and chosen destinations, you could face a range of medical and security incidents.  

International SOS can help you:
- **Monitor global risks in real time** with our Risk Information Services and **Quantum** digital platform.  
- **Support travelers 24/7** with immediate access to doctors, security experts, and interpreters.  
- **Plan for medical and security evacuations**, ensuring employees can be moved quickly and safely if needed.  
- **Fulfill your Duty of Care** by aligning with global standards like ISO 31030.  
        """)

        # Risk Outlook Section
        st.markdown("""
<div style="background-color:#f5f5f5; padding:40px; margin-top:40px; margin-bottom:40px;">
    <h2 style="text-align:center; color:#232762;">Explore the Risk Outlook 2025 Report</h2>
    <div style="display:flex; align-items:center; justify-content:center; gap:40px; flex-wrap:wrap;">
        <div style="flex:1; min-width:300px; text-align:center;">
            <img src="https://cdn1.internationalsos.com/-/jssmedia/risk-outlook-2025-report.png?w=800&h=auto&mw=800&rev=60136b946e6f46d1a8c9a458213730a7"
                 alt="Risk Outlook 2025" style="max-width:100%; height:auto; border-radius:8px;">
        </div>
        <div style="flex:1; min-width:300px;">
            <p style="font-size:16px; line-height:1.6; color:#333;">
                The <b>Risk Outlook 2025</b> is our flagship annual study, providing actionable insights into the key medical and security 
                challenges facing organizations worldwide. Developed with expert analysis and global data, it helps leaders prepare 
                for the unexpected and safeguard their workforce.
            </p>
            <p style="text-align:left; margin-top:20px;">
                <a href="https://www.internationalsos.com/risk-outlook?utm_source=riskreport" target="_blank"
                   style="background-color:white; color:#2f4696; font-weight:bold; 
                          padding:12px 24px; text-decoration:none; border:2px solid #2f4696;
                          border-radius:20px; display:inline-block;">
                    📘 Access the Risk Outlook 2025 Report
                </a>
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Bottom CTA Section
st.markdown(f"""
<div style="background-color:#232762; padding:40px; text-align:center;">
    <h2 style="color:white;">How we can support</h2>
    <p style="color:white; font-size:16px; max-width:700px; margin:auto; margin-bottom:20px;">
    Protecting your people from health and security threats. 
    Our comprehensive Travel Risk Management program supports both managers and employees by proactively 
    identifying, alerting, and managing medical, security, mental wellbeing, and logistical risks.
    </p>
    <a href="https://www.internationalsos.com/get-in-touch?utm_source=riskreport" target="_blank">
       <button style="background-color:#EF820F; color:white; font-weight:bold; 
                      border:none; padding:15px 30px; font-size:16px; cursor:pointer; 
                      margin-top:15px; border-radius:20px;">
            Get in Touch
       </button>
    </a>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center; font-size:12px; color:gray; margin-top:20px;">
© 2025 International SOS. WORLDWIDE REACH. HUMAN TOUCH.
</div>
""", unsafe_allow_html=True)
