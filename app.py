import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

@st.cache_data
def load_data():
    df = pd.read_excel("Trip and cases report 2023-2025.xlsx", sheet_name="Trips and Cases")
    df = df.rename(columns={"Country Name": "Country", "International Trips": "Trips"})
    return df

data = load_data()
case_columns = [col for col in data.columns if "Probability" in col]

st.set_page_config(page_title="International SOS Travel Risk Report", layout="wide")
st.title("🌍 International SOS Travel Risk Report")

# Input
st.markdown("### Enter Traveler Data")
countries, traveler_counts = [], []
for i in range(1, 4):
    col1, col2 = st.columns([2,1])
    with col1:
        country = st.text_input(f"Destination Country {i}", "")
    with col2:
        travelers = st.number_input(f"Travelers", min_value=0, value=0, step=1, key=f"trav{i}")
    if country:
        countries.append(country.strip())
        traveler_counts.append(travelers)

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
            case_data.update({"Country": country, "Trips": travelers, "Total Cases": total_cases})
            results.append(case_data)
        else:
            results.append({"Country": country, "Trips": travelers, "Total Cases": 0})

    results_df = pd.DataFrame(results)

    if not results_df.empty:
        total_trips = results_df["Trips"].sum()
        total_cases = results_df["Total Cases"].sum()

        # Top metrics like India.pdf
        st.metric("Trips", f"{total_trips:,}")
        st.metric("Estimated Assistance Cases", f"{total_cases:.2f}")

        tabs = st.tabs(["Overview", "Case Types", "Risks", "Glossary"])

        with tabs[0]:
            st.subheader("Country Overview")
            for _, row in results_df.iterrows():
                st.write(f"**{row['Country']}**: {row['Total Cases']:.2f} estimated cases from {row['Trips']} trips")

        with tabs[1]:
            st.subheader("Case Type Breakdown")
            case_totals = results_df.drop(columns=["Country", "Trips", "Total Cases"]).sum().reset_index()
            case_totals.columns = ["Case Type", "Estimated Cases"]
            fig = px.bar(case_totals, x="Case Type", y="Estimated Cases", text="Estimated Cases")
            st.plotly_chart(fig, use_container_width=True)

        with tabs[2]:
            st.subheader("Risks & Assistance Overview")
            st.write("Medical Risk: Variable")
            st.write("Food & Water: Unsafe")
            st.write("Disease Risk: High")
            st.write("Travel Security Risk: MEDIUM")

        with tabs[3]:
            st.subheader("Glossary of Risk Ratings")
            with st.expander("Medical Sub-Risks"):
                st.write("**Excellent**: International standard")
                st.write("**Variable**: Quality varies by location")
            with st.expander("Travel Security Sub-Risks"):
                st.write("**Protests**: Often disruptive or violent")
                st.write("**Crime**: Occurs in many areas, sometimes violent")

        # PDF Output (matching India.pdf style)
        def create_pdf(dataframe, total_cases):
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)

            c.setFont("Helvetica-Bold", 18)
            c.drawString(150, 770, "International SOS Travel Risk Report")

            c.setFont("Helvetica", 12)
            c.drawString(30, 740, f"Total Trips: {int(total_trips)}")
            c.drawString(30, 720, f"Total Estimated Assistance Cases: {total_cases:.2f}")

            y = 690
            c.setFont("Helvetica-Bold", 14)
            c.drawString(30, y, "Estimated Cases by Country")
            y -= 20
            for _, row in dataframe.iterrows():
                c.setFont("Helvetica", 12)
                c.drawString(30, y, f"{row['Country']}: {row['Total Cases']:.2f} cases ({row['Trips']} trips)")
                y -= 20

            # Disclaimer
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(30, 40, "This report is for general educational purposes only. Source: International SOS data.")
            
            c.showPage()
            c.save()
            buffer.seek(0)
            return buffer

        pdf_buffer = create_pdf(results_df, total_cases)
        st.download_button("📄 Download PDF Report", data=pdf_buffer,
                           file_name="travel_risk_report.pdf", mime="application/pdf")
