import streamlit as st
import pandas as pd
import plotly.express as px
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
# Streamlit Page Config
# -------------------------
st.set_page_config(page_title="International SOS | Assistance & Travel Risks", layout="wide")

# -------------------------
# Top Banner with Logo
# -------------------------
logo_url = "https://images.learn.internationalsos.com/EloquaImages/clients/InternationalSOS/%7Bfbdb84ee-e7f6-4acf-99bb-e59416ae6fda%7D_int.sos_logo.png"
st.markdown(f"""
<div style="background-color:#232762; padding:20px; display:flex; align-items:center;">
    <img src="{logo_url}" alt="International SOS" style="height:60px; margin-right:20px;">
    <h1 style="color:white; margin:0;">Assistance and Travel Risks Simulation Report</h1>
</div>
""", unsafe_allow_html=True)

st.write("")

# -------------------------
# Input Section
# -------------------------
st.markdown("## Step 1: Enter Traveler Data")
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

if countries:
    # -------------------------
    # Calculations
    # -------------------------
    results = []
    for country, travelers in zip(countries, traveler_counts):
        row = data[data["Country"].str.contains(country, case=False, na=False)]
        if not row.empty:
            case_data, total_cases = {}, 0
            for col in case_columns:
                prob = row.iloc[0][col]  # Excel already decimal (e.g. 0.125 for 12.5%)
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

        st.markdown("## Step 2: Estimated Assistance Needs")

        col1, col2 = st.columns([1,2])
        with col1:
            st.metric("Total Travelers", f"{total_trips:,}")
            st.metric("Total Estimated Cases", f"{total_cases:.2f}")
        with col2:
            fig = px.bar(results_df, x="Country", y="Total Cases", 
                        text=results_df["Total Cases"].round(2),
                        color="Country",
                        title="Estimated Cases by Country",
                        color_discrete_sequence=["#2f4696", "#232762", "#4a69bd"])
            st.plotly_chart(fig, use_container_width=True)

        case_totals = results_df.drop(columns=["Country", "Travelers", "Total Cases"]).sum().reset_index()
        case_totals.columns = ["Case Type", "Estimated Cases"]

        st.markdown("### Case Type Breakdown (Overall)")
        fig2 = px.pie(case_totals, values="Estimated Cases", names="Case Type",
                      color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig2, use_container_width=True)

        # -------------------------
        # Glossary Sections
        # -------------------------
        st.markdown("## Medical Sub-Risks Glossary")
        st.write("""
- **Excellent**: International standard  
- **Good**: High standard, especially in major cities  
- **Variable**: Quality varies; lower outside major cities  
- **Limited**: Specialist care limited; evacuations may be required  
- **Poor**: Basic care lacking; serious conditions require evacuation  
        """)

        st.markdown("## Travel Security Sub-Risks Glossary")
        st.write("""
- **Protests**: May be disruptive or violent  
- **Crime**: Can occur in many areas, sometimes violent  
- **Transport**: Few reliable or safe options in some areas  
- **Terrorism/Conflict**: Can pose direct risks in certain regions  
- **Natural Hazards**: Can cause significant disruption  
- **Cultural Issues**: Non-compliance may result in legal or physical consequences  
        """)

        # -------------------------
        # PDF Output
        # -------------------------
        def create_pdf(dataframe, total_cases, case_totals):
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)

            # Banner with Logo
            logo = ImageReader(requests.get(logo_url, stream=True).raw)
            c.setFillColorRGB(35/255, 39/255, 98/255)  # Banner color
            c.rect(0, 750, 612, 50, fill=True, stroke=False)
            c.drawImage(logo, 30, 755, height=40, preserveAspectRatio=True, mask='auto')
            c.setFillColorRGB(1,1,1)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(150, 770, "Assistance and Travel Risks Simulation Report")

            # Summary
            c.setFillColorRGB(0,0,0)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(30, 720, "Summary")
            c.setFont("Helvetica", 12)
            c.drawString(30, 700, f"Total Travelers: {int(dataframe['Travelers'].sum())}")
            c.drawString(30, 680, f"Total Estimated Cases: {total_cases:.2f}")
            c.drawString(30, 660, f"Countries Analyzed: {', '.join(dataframe['Country'])}")

            # Country Breakdown
            y = 630
            c.setFont("Helvetica-Bold", 14)
            c.drawString(30, y, "Estimated Cases by Country")
            y -= 20
            c.setFont("Helvetica", 12)
            for _, row in dataframe.iterrows():
                c.drawString(30, y, f"{row['Country']}: {row['Total Cases']:.2f} cases "
                                    f"(from {int(row['Travelers'])} travelers)")
                y -= 20

            # Case Types
            y -= 20
            c.setFont("Helvetica-Bold", 14)
            c.drawString(30, y, "Case Type Breakdown (Overall)")
            y -= 20
            c.setFont("Helvetica", 12)
            for _, row in case_totals.iterrows():
                c.drawString(30, y, f"{row['Case Type']}: {row['Estimated Cases']:.2f} cases")
                y -= 20

            # Glossaries
            c.showPage()
            c.setFont("Helvetica-Bold", 16)
            c.drawString(30, 770, "Medical Sub-Risks Glossary")
            c.setFont("Helvetica", 12)
            c.drawString(30, 740, "Excellent: International standard")
            c.drawString(30, 725, "Good: High standard in major cities")
            c.drawString(30, 710, "Variable: Quality varies by location")
            c.drawString(30, 695, "Limited: Specialist care limited; evacuations may be required")
            c.drawString(30, 680, "Poor: Basic care lacking; serious conditions require evacuation")

            y = 640
            c.setFont("Helvetica-Bold", 16)
            c.drawString(30, y, "Travel Security Sub-Risks Glossary")
            c.setFont("Helvetica", 12)
            c.drawString(30, y-30, "Protests: May be disruptive or violent")
            c.drawString(30, y-45, "Crime: Occurs in many areas, sometimes violent")
            c.drawString(30, y-60, "Transport: Few reliable or safe options")
            c.drawString(30, y-75, "Terrorism/Conflict: Direct risks possible")
            c.drawString(30, y-90, "Natural Hazards: Can cause significant disruption")
            c.drawString(30, y-105, "Cultural Issues: Non-compliance may result in legal/physical consequences")

            # Disclaimer
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(30, 40, "This report is for general educational purposes only. Source: International SOS data.")

            c.save()
            buffer.seek(0)
            return buffer

        pdf_buffer = create_pdf(results_df, total_cases, case_totals)
        st.download_button("📄 Step 3: Download Full PDF Report", data=pdf_buffer,
                           file_name="travel_risk_report.pdf", mime="application/pdf")
