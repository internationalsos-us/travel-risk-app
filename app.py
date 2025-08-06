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
st.write("")

# -------------------------
# Intro Section
# -------------------------
st.markdown('<h1 style="color:#232762;">Welcome to the International SOS Travel Risk Simulation Tool</h1>', unsafe_allow_html=True)
st.write("""
This tool provides a simulation of potential medical and security assistance cases based on your **trip volumes**.
It uses International SOS proprietary data collected from millions of cases globally.
""")
st.write("")
st.write("")

# -------------------------
# Input Section
# -------------------------
st.markdown('<h2 style="color:#2f4696;">Step 1: Enter Trip Volumes</h2>', unsafe_allow_html=True)
st.write("Select countries and input estimated annual trip volumes. Add more countries if needed.")
st.write("")

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
    if country and trips > 0:
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
if countries and sum(trip_counts) > 0:
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

    if not results_df.empty and results_df["Total Cases"].sum() > 0:
        total_trips = results_df["Trips"].sum()
        total_cases = results_df["Total Cases"].sum()

        st.markdown('---')
        st.markdown('<h2 style="color:#2f4696;">Step 2: Estimated Assistance Needs</h2>', unsafe_allow_html=True)
        st.write("")

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
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.write("")
        st.write("")

        # -------------------------
        # Case Type Breakdown
        # -------------------------
        st.markdown('---')
        st.markdown('<h2 style="color:#2f4696;">Case Type Breakdown</h2>', unsafe_allow_html=True)
        st.write("")

        col_user, col_bench = st.columns(2)

        # User Pie Chart
        with col_user:
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
            
            case_totals_user['Case Type'] = case_totals_user['Case Type'].apply(lambda x: x.replace(' Case Probability', ''))
            case_totals_user = case_totals_user.set_index('Case Type').reindex(case_type_colors.keys()).reset_index()
            case_totals_user = case_totals_user.dropna(subset=['Estimated Cases'])

            fig_user = px.pie(
                case_totals_user,
                values="Estimated Cases",
                names="Case Type",
                color="Case Type",
                color_discrete_map=case_type_colors,
                title="Your Estimated Case Breakdown"
            )
            fig_user.update_traces(textinfo="label+percent", textposition="outside",
                                   marker=dict(line=dict(color='rgba(0,0,0,0)', width=0)))
            fig_user.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
                                   margin=dict(t=50, b=100, l=50, r=50), uniformtext_minsize=12, uniformtext_mode='hide')
            st.plotly_chart(fig_user, use_container_width=True)

        # Benchmark Pie Chart with Styled Toggle
        with col_bench:
            if "benchmark_mode" not in st.session_state:
                st.session_state.benchmark_mode = "Global Average"
            
            # --- Button Logic for Toggling ---
            col_btn1, col_btn2 = st.columns(2)
            
            # Set the new mode based on button clicks
            if col_btn1.button("Global Average", key="global_btn_click", use_container_width=True):
                st.session_state.benchmark_mode = "Global Average"
            if col_btn2.button("Regional Average", key="regional_btn_click", use_container_width=True):
                st.session_state.benchmark_mode = "Regional Average"

            # Apply CSS styling based on the current mode
            global_class = 'toggle-selected' if st.session_state.benchmark_mode == 'Global Average' else 'toggle-unselected'
            regional_class = 'toggle-selected' if st.session_state.benchmark_mode == 'Regional Average' else 'toggle-unselected'
            
            st.markdown(f"""
            <style>
                div[data-testid="stColumn"]:nth-child(2) > div > button[data-testid="base-button-secondary"]:nth-child(1) {{
                    background-color: {'#2f4696' if st.session_state.benchmark_mode == 'Global Average' else '#cccccc'};
                    color: {'white' if st.session_state.benchmark_mode == 'Global Average' else 'black'};
                }}
                div[data-testid="stColumn"]:nth-child(2) > div > button[data-testid="base-button-secondary"]:nth-child(2) {{
                    background-color: {'#2f4696' if st.session_state.benchmark_mode == 'Regional Average' else '#cccccc'};
                    color: {'white' if st.session_state.benchmark_mode == 'Regional Average' else 'black'};
                }}
            </style>
            """, unsafe_allow_html=True)
            # --- End Button Logic ---
            
            st.write("") # Add some space below buttons

            if st.session_state.benchmark_mode == "Global Average":
                case_totals_bench = data[case_columns].mean().reset_index()
                case_totals_bench.columns = ["Case Type", "Benchmark Cases"]
                case_totals_bench["Benchmark Cases"] = case_totals_bench["Benchmark Cases"] * total_trips
                benchmark_title = "Global Average Case Breakdown"
            else:
                available_regions = sorted(data["Region"].dropna().unique())
                if available_regions:
                    primary_region = region_mapping.get(countries[0]) if countries and countries[0] in region_mapping else available_regions[0]
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

            case_totals_bench['Case Type'] = case_totals_bench['Case Type'].apply(lambda x: x.replace(' Case Probability', ''))
            case_totals_bench = case_totals_bench.set_index('Case Type').reindex(case_type_colors.keys()).reset_index()
            case_totals_bench = case_totals_bench.dropna(subset=['Benchmark Cases'])

            fig_bench = px.pie(
                case_totals_bench,
                values="Benchmark Cases",
                names="Case Type",
                color="Case Type",
                color_discrete_map=case_type_colors,
                title=benchmark_title
            )
            fig_bench.update_traces(textinfo="label+percent", textposition="outside",
                                    marker=dict(line=dict(color='rgba(0,0,0,0)', width=0)))
            fig_bench.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
                                    margin=dict(t=50, b=100, l=50, r=50), uniformtext_minsize=12, uniformtext_mode='hide')
            st.plotly_chart(fig_bench, use_container_width=True)

        st.write("")
        st.write("")
        
        # -------------------------
        # Recommendations Section (moved up)
        # -------------------------
        st.markdown('---')
        st.markdown('<h2 style="color:#2f4696;">What These Results Mean for You</h2>', unsafe_allow_html=True)
        st.write("")
        st.write("""
Based on your trip volumes and chosen destinations, you could face a range of medical and security incidents.  
International SOS can help you:
- **Monitor global risks in real time** with our Risk Information Services and **Quantum** digital platform.  
- **Support travelers 24/7** with immediate access to doctors, security experts, and interpreters.  
- **Plan for medical and security evacuations**, ensuring employees can be moved quickly and safely if needed.  
- **Fulfill your Duty of Care** by aligning with global standards like ISO 31030.  
        """)

        st.write("")
        st.write("")

        # -------------------------
        # Risk Outlook section (moved down)
        # -------------------------
        st.markdown('---')
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
                           style="background-color:#2f4696; color:white; font-weight:bold;
                                  padding:12px 24px; text-decoration:none; border-radius:8px;">
                            📘 Access the Risk Outlook 2025 Report
                        </a>
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
st.markdown('---')
st.write("")

# -------------------------
# Get in Touch Section
# -------------------------
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

st.write("")
st.write("")

# Footer
st.markdown("""
<div style="text-align:center; font-size:12px; color:gray; margin-top:20px;">
© 2025 International SOS. WORLDWIDE REACH. HUMAN TOUCH.
</div>
""", unsafe_allow_html=True)
