import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
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
logo_url = "https://images.learn.internationalsos.com/EloquaImages/clients/InternationalSOS/%7B0769a7db-dae2-4ced-add6-d1a73cb775d5%7D_International_SOS_white_hr_%281%29.png"
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
                prob = row.iloc[0][col]  # Excel already decimal
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
        brand_colors = ["#2f4696", "#009354", "#FFD744", "#DD2484", "#6988C0", "#6C206B", "#EF820F", "#D4002C", "#EEEFEF"]
        fig2 = px.pie(case_totals, values="Estimated Cases", names="Case Type",
                      color_discrete_sequence=brand_colors)
        st.plotly_chart(fig2, use_container_width=True)

        # -------------------------
        # Glossary Sections
        # -------------------------
        st.markdown("## Glossaries")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<h3 style="color:#2f4696;">Medical Sub-Risks Glossary</h3>', unsafe_allow_html=True)
            st.write("""
- **Excellent**: International standard  
- **Good**: High standard, especially in major cities  
- **Variable**: Quality varies; lower outside major cities  
- **Limited**: Specialist care limited; evacuations may be required  
- **Poor**: Basic care lacking; serious conditions require evacuation  
            """)

        with col2:
            st.markdown('<h3 style="color:#009354;">Travel Security Sub-Risks Glossary</h3>', unsafe_allow_html=True)
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
            c.setFillColorRGB(35/255, 39/255, 98/255)
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

            # Charts
            # Country Bar Chart
            plt.figure(figsize=(5,3))
            plt.bar(dataframe["Country"], dataframe["Total Cases"], color="#2f4696")
            plt.title("Estimated Cases by Country")
            plt.tight_layout()
            bar_buf = BytesIO()
            plt.savefig(bar_buf, format="png")
            bar_buf.seek(0)
            c.drawImage(ImageReader(bar_buf), 50, 400, width=500, height=200)

            # Pie Chart
            plt.figure(figsize=(5,3))
            plt.pie(case_totals["Estimated Cases"], labels=case_totals["Case Type"], autopct="%.1f%%",
                    colors=brand_colors[:len(case_totals)])
            plt.title("Case Type Breakdown (Overall)")
            pie_buf = BytesIO()
            plt.savefig(pie_buf, format="png")
            pie_buf.seek(0)
            c.drawImage(ImageReader(pie_buf), 50, 150, width=500, height=200)

            c.showPage()

            # Glossaries
            c.setFont("Helvetica-Bold", 16)
            c.setFillColorRGB(47/255,70/255,150/255)  # Medical color
            c.drawString(30, 770, "Medical Sub-Risks Glossary")
            c.setFillColorRGB(0,0,0)
            c.setFont("Helvetica", 12)
            c.drawString(30, 740, "Excellent: International standard")
            c.drawString(30, 725, "Good: High standard in major cities")
            c.drawString(30, 710, "Variable: Quality varies by location")
            c.drawString(30, 695, "Limited: Specialist care limited; evacuations may be required")
            c.drawString(30, 680, "Poor: Basic care lacking; serious conditions require evacuation")

            c.setFillColorRGB(0/255,147/255,84/255)  # Security color
            c.setFont("Helvetica-Bold", 16)
            c.drawString(300, 770, "Travel Security Sub-Risks Glossary")
            c.setFillColorRGB(0,0,0)
            c.setFont("Helvetica", 12)
            y = 740
            glossary_items = [
                "Protests: May be disruptive or violent",
                "Crime: Occurs in many areas, sometimes violent",
                "Transport: Few reliable or safe options",
                "Terrorism/Conflict: Direct risks possible",
                "Natural Hazards: Can cause significant disruption",
                "Cultural Issues: Non-compliance may result in consequences"
            ]
            for item in glossary_items:
                c.drawString(300, y, item)
                y -= 20

            # Disclaimer
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(30, 40, "This report is for educational purposes only. Actual assistance cases may vary.")
            c.drawString(30, 30, "Source: International SOS data.")

            c.save()
            buffer.seek(0)
            return buffer

        pdf_buffer = create_pdf(results_df, total_cases, case_totals)
        st.download_button("📄 Download the PDF Report", data=pdf_buffer,
                           file_name="travel_risk_report.pdf", mime="application/pdf",
                           use_container_width=True,
                           key="pdf_download")

        # Custom styling for download button
        st.markdown("""
        <style>
        div[data-testid="stDownloadButton"] button {
            background-color: #2f4696;
            color: white;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

# -------------------------
# Bottom CTA Section
# -------------------------
st.markdown(f"""
<div style="background-color:#232762; padding:40px; text-align:center;">
    <h2 style="color:white;">How we can support</h2>
    <p style="color:white; font-size:16px; max-width:700px; margin:auto;">
    Protecting your people from health and security threats. 
    Our comprehensive Travel Risk Management program supports both managers and employees by proactively 
    identifying, alerting, and managing medical, security, mental wellbeing, and logistical risks.
    </p>
    <a href="https://www.internationalsos.com/get-in-touch?utm_source=riskreport" 
       target="_blank">
       <button style="background-color:#EF820F; color:white; font-weight:bold; 
                      border:none; padding:15px 30px; font-size:16px; cursor:pointer;">
            Get in Touch
       </button>
    </a>
</div>
""", unsafe_allow_html=True)
