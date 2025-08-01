import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# -------------------------
# Load and Preprocess Data
# -------------------------
@st.cache_data
def load_data():
    raw_df = pd.read_excel("Trip and cases report 2023-2025.xlsx", sheet_name="Trips and Cases")
    
    # Clean headers
    raw_df.columns = raw_df.iloc[0]
    raw_df = raw_df.drop(0)

    # Rename columns
    raw_df = raw_df.rename(columns={"Country Name": "Country", "International Trips": "Trips"})

    # Ensure numeric conversion
    numeric_cols = raw_df.columns.drop("Country")
    raw_df[numeric_cols] = raw_df[numeric_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

    # Calculate totals
    raw_df["Total Cases"] = raw_df[numeric_cols].sum(axis=1)
    raw_df["Cases per Traveler"] = raw_df["Total Cases"] / raw_df["Trips"].replace(0, pd.NA)

    return raw_df[["Country", "Cases per Traveler"]]

data = load_data()

# -------------------------
# Streamlit App UI
# -------------------------
st.set_page_config(page_title="Travel Risk Probability Calculator", layout="centered")
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
        travelers = st.number_input(f"Number of Travelers for {country or f'Country {i}'}", min_value=0, value=0, step=1)
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
        prob_per_traveler = row.iloc[0]["Cases per Traveler"]
        estimated_cases = travelers * prob_per_traveler
        results.append({"Country": country, "Travelers": travelers, "Estimated Cases": estimated_cases})
    else:
        results.append({"Country": country, "Travelers": travelers, "Estimated Cases": 0})

results_df = pd.DataFrame(results)

if not results_df.empty and results_df["Travelers"].sum() > 0:
    st.subheader("Results Overview")
    total_cases = results_df["Estimated Cases"].sum()
    st.metric("Total Estimated Cases", f"{total_cases:.0f}")

    # Bar chart by country
    fig = px.bar(results_df, x="Country", y="Estimated Cases", text=results_df["Estimated Cases"].round(0),
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
        c.setFont("Helvetica-Bold", 16)
        c.drawString(30, 770, "Travel Risk Probability Report")
        c.setFont("Helvetica", 12)
        c.drawString(30, 740, f"Total Estimated Cases: {int(total_cases)}")
        y = 710
        for _, row in dataframe.iterrows():
            c.drawString(30, y, f"{row['Country']}: {int(row['Estimated Cases'])} cases "
                                f"from {int(row['Travelers'])} travelers")
            y -= 20
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    pdf_buffer = create_pdf(results_df, total_cases)
    st.download_button("📄 Download Full PDF Report", data=pdf_buffer, 
                       file_name="travel_risk_report.pdf", mime="application/pdf")
