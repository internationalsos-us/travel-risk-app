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
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Travel Risk Probability Calculator", layout="wide")
st.title("🌍 Travel Risk Probability Calculator")
st.write("Estimate potential assistance cases by country and case type.")

st.header("Enter Traveler Information")
countries = []
traveler_counts = []

for i in range(1, 4):
    col1, col2 = st.columns(2)
    with col1:
        country = st.text_input(f"Country {i}", "")
    with col2:
        travelers = st.number_input(f"Number of Travelers for {country or f'Country {i}'}",
                                    min_value=0, value=0, step=1)
    if country:
        countries.append(country.strip())
        traveler_counts.append(travelers)

# -------------------------
# Calculations
# -------------------------
results = []
for country, travelers in zip(countries, traveler_counts):
    row = data[data["Country"].str.contains(country, case=False, na=False)]
    if not row.empty:
        case_data = {}
        total_cases = 0
        for col in case_columns:
            prob = row.iloc[0][col]  # Already a decimal (e.g., 0.125 for 12.5%)
            estimated = travelers * prob  # ✅ Correct: no /100
            case_data[col.replace(" Case Probability", "")] = estimated
            total_cases += estimated
        case_data.update({"Country": country, "Travelers": travelers, "Total Cases": total_cases})
        results.append(case_data)
    else:
        results.append({"Country": country, "Travelers": travelers, "Total Cases": 0})

results_df = pd.DataFrame(results)

if not results_df.empty and results_df["Travelers"].sum() > 0:
    st.subheader("Results Overview")
    total_cases = results_df["Total Cases"].sum()
    st.metric("Total Estimated Cases", f"{total_cases:.2f}")

    # Bar chart by country
    fig = px.bar(results_df, x="Country", y="Total Cases", 
                 text=results_df["Total Cases"].round(2),
                 title="Estimated Cases by Country")
    st.plotly_chart(fig, use_container_width=True)

    # Case-type breakdown overall
    case_totals = results_df[results_df.columns.difference(["Country", "Travelers", "Total Cases"])] \
        .sum().reset_index()
    case_totals.columns = ["Case Type", "Estimated Cases"]

    fig2 = px.pie(case_totals, values="Estimated Cases", names="Case Type", 
                  title="Case Type Breakdown (Overall)")
    st.plotly_chart(fig2, use_container_width=True)

    # -------------------------
    # PDF Report Download
    # -------------------------
    def create_pdf(dataframe, total_cases, case_totals):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Header
        c.setFont("Helvetica-Bold", 18)
        c.drawString(150, 770, "Travel Risk Probability Report")
        c.setFont("Helvetica", 12)
        c.drawString(30, 740, "This report estimates potential assistance cases based on traveler data.")
        
        # Summary
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, 710, "Summary")
        c.setFont("Helvetica", 12)
        c.drawString(30, 690, f"Total Estimated Cases: {total_cases:.2f}")
        c.drawString(30, 670, f"Countries Analyzed: {', '.join(dataframe['Country'])}")

        # Breakdown by country
        y = 640
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y, "Estimated Cases by Country")
        c.setFont("Helvetica", 12)
        y -= 20
        for _, row in dataframe.iterrows():
            c.drawString(30, y, f"{row['Country']}: {row['Total Cases']:.2f} cases "
                                f"from {int(row['Travelers'])} travelers")
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
    st.download_button("📄 Download Full PDF Report", data=pdf_buffer, 
                       file_name="travel_risk_report.pdf", mime="application/pdf")
