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
    df = df.rename(columns={"Country Name": "Country"})  # adjust if needed
    return df

data = load_data()

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Travel Risk Probability Calculator", layout="wide")
st.title("🌍 Travel Risk Probability Calculator")
st.write("Estimate potential assistance cases based on your travelers.")

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
        # Sum all probability columns (you may break this down by case type later)
        case_prob = row.drop(columns=["Country"]).sum(axis=1).values[0]
        estimated_cases = travelers * (case_prob / 100)  # percentages in Excel
        results.append({"Country": country, "Travelers": travelers, 
                        "Estimated Cases": estimated_cases})
    else:
        results.append({"Country": country, "Travelers": travelers, "Estimated Cases": 0})

results_df = pd.DataFrame(results)

if not results_df.empty and results_df["Travelers"].sum() > 0:
    st.subheader("Results Overview")
    total_cases = results_df["Estimated Cases"].sum()
    st.metric("Total Estimated Cases", f"{total_cases:.0f}")

    # Bar chart by country
    fig = px.bar(results_df, x="Country", y="Estimated Cases", 
                 text=results_df["Estimated Cases"].round(0),
                 title="Estimated Cases by Country")
    st.plotly_chart(fig, use_container_width=True)

    # Pie chart distribution
    fig2 = px.pie(results_df, values="Estimated Cases", names="Country", 
                  title="Case Distribution by Country")
    st.plotly_chart(fig2, use_container_width=True)

    # -------------------------
    # PDF Report Download
    # -------------------------
    def create_pdf(dataframe, total_cases):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # Header
        c.setFont("Helvetica-Bold", 18)
        c.drawString(200, 770, "Travel Risk Probability Report")
        c.setFont("Helvetica", 12)
        c.drawString(30, 740, "This report estimates potential assistance cases based on your traveler data.")
        
        # Summary
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, 710, "Summary")
        c.setFont("Helvetica", 12)
        c.drawString(30, 690, f"Total Estimated Cases: {int(total_cases)}")
        c.drawString(30, 670, f"Countries Analyzed: {', '.join(dataframe['Country'])}")

        # Breakdown
        y = 640
        c.setFont("Helvetica-Bold", 14)
        c.drawString(30, y, "Estimated Cases by Country")
        y -= 20
        c.setFont("Helvetica", 12)
        for _, row in dataframe.iterrows():
            c.drawString(30, y, f"{row['Country']}: {int(row['Estimated Cases'])} cases "
                                f"from {int(row['Travelers'])} travelers")
            y -= 20

        # Footer disclaimer
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(30, 50, "This report is for general educational purposes only and uses probability models.")
        c.drawString(30, 40, "Actual assistance cases may vary. Source: International SOS data.")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    pdf_buffer = create_pdf(results_df, total_cases)
    st.download_button("📄 Download Full PDF Report", data=pdf_buffer, 
                       file_name="travel_risk_report.pdf", mime="application/pdf")
