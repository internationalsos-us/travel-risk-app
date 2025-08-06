import streamlit as st
import pandas as pd
import plotly.express as px

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
# Color Mapping
# -------------------------
case_type_colors = {
    "Medical Information & Analysis": "#2f4696",
    "Medical Out-Patient": "#6988C0",
    "Medical In-Patient": "#FFD744",
    "Medical Evacs, Repats, & RMR": "#DD2484",
    "Security Evacs, Repats, & RMR": "#6C206B",
    "Security Information & Analysis": "#009354",
    "Security Referral": "#EF820F",
    "Security Interventional Assistance": "#D4002C",
    "Security Evacuation": "#EEEFEF",
    "Travel Information & Analysis": "#232762"
}

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
.toggle-bar {
    display: flex;
    justify-content: center;
    margin-bottom: 15px;
    height: 50px; /* fix toggle height */
    align-items: center;
}
.toggle-btn {
    padding: 8px 18px;
    border-radius: 20px;
    border: none;
    cursor: pointer;
    margin: 0 5px;
    font-weight: bold;
    font-size: 14px;
}
.toggle-selected {
    background-color: #2f4696;
    color: white;
}
.toggle-unselected {
    background-color: #cccccc;
    color: black;
}
.fixed-dropdown {
    height: 50px; /* fix dropdown height */
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
This tool provides a simulation of potential medical and security assistance cases based on your **trip volumes**.
It uses International SOS proprietary data collected from millions of cases globally.
""")

# -------------------------
# Input Section
# -------------------------
st.markdown('<h2 style="color:#2f4696;">Step 1: Enter Trip Volumes</h2>', unsafe_allow_html=True)
st.write("Select countries and input estimated annual trip volumes. Add more countries if needed.")

countries, trip_counts = [], []
country_options = sorted(data["Country"].dropna().unique())

if "num_rows" not in st.session_state:
    st.session_state.num_rows = 3

for i in range(1, st.session_state.num_rows + 1):
    col1, col2 = st.columns([2,1])
    with col1:
        country = st.selectbox(f"Destination Country {i}", [""] + list(country_options), key=f"country{i}")
    with col2:
        trips = st.number_input(f"Trips for {country or f'Country {i}'}",
                                min_value=0, value=0, step=1, key=f"trav{i}")
    if country:
        countries.append(country)
        trip_counts.append(trips)

# Add/Remove buttons
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
# Region Mapping
# -------------------------
region_mapping = {
    "Afghanistan": "South Asia", "Azerbaijan": "Europe & Central Asia", "Bangladesh": "South Asia",
    "Benin": "Sub-Saharan Africa", "Brazil": "Latin America & Caribbean", "China": "East Asia & Pacific",
    "Egypt": "Middle East & North Africa", "France": "Europe & Central Asia",
    "India": "South Asia", "Japan": "East Asia & Pacific", "Kenya": "Sub-Saharan Africa",
    "Mexico": "Latin America & Caribbean", "Nigeria": "Sub-Saharan Africa",
    "Pakistan": "South Asia", "South Africa": "Sub-Saharan Africa", "United States": "North America",
    "United Kingdom": "Europe & Central Asia"
}
data["Region"] = data["Country"].map(region_mapping)

# -------------------------
# Results Section
# -------------------------
if countries and sum(trip_counts) > 0: # Check if countries are selected AND trips > 0
    results = []
    for country, trips in zip(countries, trip_counts):
        row = data[data["Country"].str.contains(country, case=False, na=False)]
        if not row.empty:
            case_data, total_cases = {}, 0
            for col in case_columns:
                prob = row.iloc[0][col]
                estimated = trips * prob
                case_data[col.replace(" Case Probability", "")] = estimated
                total_cases += estimated
            case_data.update({"Country": country, "Trips": trips, "Total Cases": total_cases})
            results.append(case_data)
        else:
            results.append({"Country": country, "Trips": trips, "Total Cases": 0})

    results_df = pd.DataFrame(results)

    if not results_df.empty and results_df["Total Cases"].sum() > 0: # Ensure there are cases to display
        total_trips = results_df["Trips"].sum()
        total_cases = results_df["Total Cases"].sum()

        st.markdown('---')
        st.markdown('<h2 style="color:#2f4696;">Step 2: Estimated Assistance Needs</h2>', unsafe_allow_html=True)

        col1, col2 = st.columns([1,2])
        with col1:
            st.metric("Total Trips", f"{total_trips:,}")
            st.metric("Total Estimated Cases", f"{total_cases:.2f}")
            st.info("Probabilities are based on the likelihood of assistance cases **per trip**.")
        with col2:
            fig = px.bar(results_df, x="Country", y="Total Cases",
                         text=results_df["Total Cases"].round(2),
                         title="Estimated Cases by Country",
                         color_discrete_sequence=["#2f4696", "#232762", "#4a69bd"])
            fig.update_layout(showlegend=False) # The `color` parameter with `color_discrete_sequence` creates a legend that isn't useful in this context, so we remove it.
            st.plotly_chart(fig, use_container_width=True)

        # -------------------------
        # Case Type Breakdown
        # -------------------------
        st.markdown('---')
        st.markdown('<h2 style="color:#2f4696;">Case Type Breakdown</h2>', unsafe_allow_html=True)

        col_user, col_bench = st.columns(2)

        # User Pie Chart
        with col_user:
            # Fixing the dropdown height by moving it outside the fixed-dropdown div
            filter_country = st.selectbox("Filter to one country (optional)", ["All"] + list(results_df["Country"]))
            
            if filter_country == "All":
                case_totals_user = results_df.drop(columns=["Country", "Trips", "Total Cases"]).sum().reset_index()
                case_totals_user.columns = ["Case Type", "Estimated Cases"]
            else:
                country_data = results_df[results_df["Country"] == filter_country].drop(
                    columns=["Country", "Trips", "Total Cases"]
                ).T.reset_index()
                country_data.columns = ["Case Type", "Estimated Cases"]
                case_totals_user = country_data
            
            # Reorder the DataFrame to match the color mapping for consistency
            case_totals_user['Case Type'] = case_totals_user['Case Type'].apply(lambda x: x.replace(' Case Probability', ''))
            case_totals_user = case_totals_user.set_index('Case Type').reindex(case_type_colors.keys()).reset_index()
            case_totals_user = case_totals_user.dropna(subset=['Estimated Cases'])


            fig_user = px.pie(
                case_totals_user,
                values="Estimated Cases",
                names="Case Type",
                color="Case Type",
                color_discrete_map=case_type_colors, # The color map is now correctly applied
                title="Your Estimated Case Breakdown"
            )
            fig_user.update_traces(textinfo="percent+label")
            fig_user.update_layout(legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"))
            st.plotly_chart(fig_user, use_container_width=True)

        # Benchmark Pie Chart with Styled Toggle
        with col_bench:
            if "benchmark_mode" not in st.session_state:
                st.session_state.benchmark_mode = "Global Average"

            # Use st.columns to place the buttons side-by-side
            btn_col1, btn_col2 = st.columns([1,1])
            
            with btn_col1:
                # Add CSS classes to buttons based on the session state
                global_btn_class = "toggle-selected" if st.session_state.benchmark_mode == "Global Average" else "toggle-unselected"
                if st.button("Global Average", key="global_btn", help="Click to view global average benchmark"):
                    st.session_state.benchmark_mode = "Global Average"
                    st.rerun() # Use rerun to update the chart immediately
            
            with btn_col2:
                regional_btn_class = "toggle-selected" if st.session_state.benchmark_mode == "Regional Average" else "toggle-unselected"
                if st.button("Regional Average", key="regional_btn", help="Click to view regional average benchmark"):
                    st.session_state.benchmark_mode = "Regional Average"
                    st.rerun() # Use rerun to update the chart immediately

            # Re-creating the buttons with the correct styling logic
            st.markdown(f"""
            <div class="toggle-bar">
                <button class="toggle-btn {global_btn_class}" onclick="window.parent.postMessage('streamlit:rerun', '*')">Global Average</button>
                <button class="toggle-btn {regional_btn_class}" onclick="window.parent.postMessage('streamlit:rerun', '*')">Regional Average</button>
            </div>
            """, unsafe_allow_html=True)
            
            # The logic to determine the benchmark data remains the same
            if st.session_state.benchmark_mode == "Global Average":
                case_totals_bench = data[case_columns].mean().reset_index()
                case_totals_bench.columns = ["Case Type", "Benchmark Cases"]
                case_totals_bench["Benchmark Cases"] = case_totals_bench["Benchmark Cases"] * total_trips
                benchmark_title = "Global Average Case Breakdown"
            else:
                available_regions = sorted(data["Region"].dropna().unique())
                # Add a conditional check to ensure a region is available
                if available_regions:
                    # Let's find the primary region from the user's input, or default to the first available one
                    primary_region = region_mapping.get(countries[0]) if countries else available_regions[0]
                    default_index = available_regions.index(primary_region) if primary_region in available_regions else 0
                    selected_region = st.selectbox("Select a region", available_regions, index=default_index, key="region_select")
                    region_avg = data[data["Region"] == selected_region][case_columns].mean()
                    case_totals_bench = region_avg.reset_index()
                    case_totals_bench.columns = ["Case Type", "Benchmark Cases"]
                    case_totals_bench["Benchmark Cases"] = case_totals_bench["Benchmark Cases"] * total_trips
                    benchmark_title = f"{selected_region} Average Case Breakdown"
                else:
                    st.warning("No region data available for benchmarking.")
                    case_totals_bench = pd.DataFrame(columns=["Case Type", "Benchmark Cases"])
                    benchmark_title = "Regional Average Case Breakdown"

            # Reorder the DataFrame to match the color mapping for consistency
            case_totals_bench['Case Type'] = case_totals_bench['Case Type'].apply(lambda x: x.replace(' Case Probability', ''))
            case_totals_bench = case_totals_bench.set_index('Case Type').reindex(case_type_colors.keys()).reset_index()
            case_totals_bench = case_totals_bench.dropna(subset=['Benchmark Cases'])

            fig_bench = px.pie(
                case_totals_bench,
                values="Benchmark Cases",
                names="Case Type",
                color="Case Type",
                color_discrete_map=case_type_colors, # Corrected the color map
                title=benchmark_title
            )
            fig_bench.update_traces(textinfo="percent+label")
            fig_bench.update_layout(legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"))
            st.plotly_chart(fig_bench, use_container_width=True)

        # -------------------------
        # Risk Outlook section
        # -------------------------
        st.markdown('---')
        st.markdown('<h2 style="color:#2f4696;">Risk Outlook</h2>', unsafe_allow_html=True)
        # Assuming you want to add some logic here to generate dynamic content
        # For now, let's add some placeholder text
        st.write("""
        This section can be used to display dynamic risk information based on the selected countries.
        For example, you could highlight the top medical and security risks for each country.
        """)
        
        # Recommendations Section
        st.markdown('---')
        st.markdown('<h2 style="color:#2f4696;">What These Results Mean for You</h2>', unsafe_allow_html=True)
        st.write("""
Based on your trip volumes and chosen destinations, you could face a range of medical and security incidents.  
International SOS can help you:
- **Monitor global risks in real time** with our Risk Information Services and **Quantum** digital platform.  
- **Support travelers 24/7** with immediate access to doctors, security experts, and interpreters.  
- **Plan for medical and security evacuations**, ensuring employees can be moved quickly and safely if needed.  
- **Fulfill your Duty of Care** by aligning with global standards like ISO 31030.  
        """)

# The 'Get in Touch' section is now moved out of the `if countries:` block
# so it always appears. This is a crucial fix for the logic.
# -------------------------
# Get in Touch Section
# -------------------------
st.markdown('---')
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
