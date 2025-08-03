import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

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
# Custom Page Config
# -------------------------
st.set_page_config(page_title="International SOS | Travel Risk Calculator", layout="wide")

# -------------------------
# Header Section
# -------------------------
st.markdown("""
<style>
.report-title {
    font-size:36px;
    font-weight:700;
    color:#0A2540;
}
.sub-title {
    font-size:20px;
    color:#1C4E80;
}
.section-header {
    font-size:24px;
    margin-top:30px;
    color:#0A2540;
}
.footer-note {
    font-size:12px;
    color:gray;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="report-title">🌍 International SOS Travel Risk Calculator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Estimate potential medical and security assistance cases for your travelers</div>', unsafe_allow_html=True)
st.markdown("---")

# -------------------------
# Input Section
# -------------------------
st.markdown('<div class="section-header">Step 1: Enter Traveler Data</div>', unsafe_allow_html=True)
st.write("Provide up to three destination countries with expected traveler volumes.")

countries, traveler_counts = [], []
for i in range(1, 4):
    col1, col2 = st.columns([2,1])
    with col1:
        country = st.text_input(f"Destination Country {i}", "")
    with col2:
        travelers = st.number_input(f"Travelers for {country or f'Country {i}'}",
                                    min_value=0, value=0, step=1, key=f"trav{i}")
    if country:
        countries.append(country.strip())
        traveler_counts.append(travelers)

# -------------------------
# Results Section
# -------------------------
if countries:
    st.markdown('<div class="section-header">Step 2: Estimated Assistance Needs</div>', unsafe_allow_html=True)

    results = []
    for country, travelers in zip(countries, traveler_counts):
        row = data[data["Country"].str.contains(country, case=False, na=False)]
        if not row.empty:
            case_data = {}
            total_cases = 0
            for col in case_columns:
                prob = row.iloc[0][col]  # already a decimal from Excel
                estimated = travelers * prob
                case_data[col.replace(" Case Probability", "")] = estimated
                total_cases += estimated
            case_data.update({"Country": country, "Travelers": travelers, "Total Cases": total_cases})
            results.append(case_data)
        else:
            results.append({"Country": country, "Travelers": travelers, "Total Cases": 0})

    results_df = pd.DataFrame(results)

    if not results_df.empty and results_df["Travelers"].sum() > 0:
        total_cases = results_df["Total Cases"].sum()

        col1, col2 = st.columns([1,2])
        with col1:
            st.metric("Total Travelers", f"{results_df['Travelers'].sum():,}")
            st.metric("Total Estimated Cases", f"{total_cases:.2f}")

        with col2:
            fig = px.bar(results_df, x="Country", y="Total Cases", 
                        text=results_df["Total Cases"].round(2),
                        color="Country",
                        title="Estimated Cases by Country")
            st.plotly_chart(fig, use_container_width=True)

        case_totals = results_df[results_df.columns.difference(["Country", "Travelers", "Total Cases"])] \
            .sum().reset_index()
        case_totals.columns = ["Case Type", "Estimated Cases"]

        st.markdown('<div class="section-header">Case Type Breakdown (Overall)</div>', unsafe_allow_html=True)
        fig2 = px.pie(case_totals, values="Estimated Cases", names="Case Type",
                      color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig2, use_container_width=True)

        # -------------------------
        # PDF Report
        # -------------------------
        def create_pdf(dataframe, total_cases, case_totals):
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)

            # Header
            c.setFont("Helvetica-Bold", 18)
            c.drawString(120, 770, "International SOS Travel Risk Report")
            c.setFont("Helvetica", 12)
            c.drawString(30, 740, "This report provides estimated assistance cases based on your traveler volumes.")

            # Summary
            c.setFont("Helvetica-Bold", 14)
            c.drawString(30, 710, "Summary")
            c.setFont("Helvetica", 12)
            c.drawString(30, 690, f"Total Travelers: {int(dataframe['Travelers'].sum())}")
            c.drawString(30, 670, f"Total Estimated Cases: {total_cases:.2f}")
            c.drawString(30, 650, f"Countries Analyzed: {', '.join(dataframe['Country'])}")

            # Breakdown by country
            y = 620
            c.setFont("Helvetica-Bold", 14)
            c.drawString(30, y, "Estimated Cases by Country")
            y -= 20
            c.setFont("Helvetica", 12)
            for _, row in dataframe.iterrows():
                c.drawString(30, y, f"{row['Country']}: {row['Total Cases']:.2f} cases "
                                    f"(from {int(row['Travelers'])} travelers)")
                y -= 20

            # Case type overview
            y -= 20
            c.setFont("Helvetica-Bold", 14)
            c.drawString(30, y, "Case Type Breakdown (Overall)")
            y -= 20
            c.setFont("Helvetica", 12)
            for _, row in case_totals.iterrows():
                c.drawString(30, y, f"{row['Case Type']}: {row['Estimated Cases']:.2f} cases")
                y -= 20

            # Footer disclaimer
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(30, 40, "This report is for educational purposes only. Actual assistance cases may vary.")
            c.drawString(30, 30, "Source: International SOS data.")

            c.showPage()
            c.save()
            buffer.seek(0)
            return buffer

        pdf_buffer = create_pdf(results_df, total_cases, case_totals)
        st.download_button("📄 Step 3: Download Full PDF Report", data=pdf_buffer,
                           file_name="travel_risk_report.pdf", mime="application/pdf")

# Footer
st.markdown("---")
st.markdown('<div class="footer-note">© 2025 International SOS. All rights reserved.</div>', unsafe_allow_html=True)
