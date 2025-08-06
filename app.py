import streamlit as st

import pandas as pd

import plotly.express as px

import plotly.graph_objects as go

import numpy as np



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

# Mapping of Case Types to Services

# -------------------------

case_type_services = {

    "Medical Information & Analysis": "Quantum digital platform for proactive risk intelligence and Medical Consulting for expert advice.",

    "Medical Out-Patient": "Medical Consulting and our extensive Provider Network for immediate access to care.",

    "Medical In-Patient": "Our TeleConsultation services, combined with expert in-patient case management.",

    "Medical Evacs, Repats, & RMR": "Dedicated Medical Evacuation and Repatriation teams with full Case Management.",

    "Security Evacs, Repats, & RMR": "Specialized Security Evacuation and Repatriation with our Security Consulting.",

    "Security Information & Analysis": "Quantum for real-time threat intelligence and expert Security Consulting.",

    "Security Referral": "Our global Provider Network and Security Consulting for reliable local support.",

    "Security Interventional Assistance": "Immediate on-the-ground support with Security Consulting and On-the-Ground Response.",

    "Security Evacuation": "Critical Security Evacuation and Repatriation services to ensure safe transport.",

    "Travel Information & Analysis": "Quantum and our Risk Ratings to help you stay ahead of potential travel disruptions."

}



# -------------------------

# Page Config

# -------------------------

st.set_page_config(page_title="International SOS | Assistance & Travel Risks", layout="wide")



# -------------------------

# Banner with new image and layout

# -------------------------

st.markdown("""

<style>

/* Global font settings */

html, body, [data-testid="stText"], [data-testid="stMarkdownContainer"] {

    font-family: Arial, sans-serif;

}

h1 {

    font-family: "Arial Black", Gadget, sans-serif;

}

h2, strong, b {

    font-family: Arial, sans-serif;

    font-weight: bold;

}

/* Banner with image background and overlay */

.main-banner {

    position: relative;

    height: 350px;

    width: 100%;

    background-image: url('https://cdn1.internationalsos.com/-/jssmedia/images/mobility-and-travel/female-traveller-checking-assistance-app-desktop/assistance-app-homepage-carousel.jpg?w=2000&h=auto&mw=2000&rev=1b9b43d76cc94fc09d199cbe40e277a6');

    background-size: cover;

    background-position: center;

    color: white;

    display: flex;

    flex-direction: column;

    justify-content: space-between;

    padding: 20px;

    box-sizing: border-box;

}

.banner-overlay {

    position: absolute;

    top: 0;

    left: 0;

    width: 100%;

    height: 100%;

    background: rgba(47, 70, 150, 0.5); /* Corporate blue overlay */

    z-index: 1;

}

.banner-content {

    position: relative;

    z-index: 2;

    display: flex;

    flex-direction: column;

    justify-content: space-between; /* Adjusted to space out content */

    height: 100%;

}

.top-header {

    display: flex;

    justify-content: flex-end; /* Align logo to the right */

    align-items: center;

    padding: 0 10px;

    margin-bottom: 20px;

}

.logo-and-title {

    display: flex;

    align-items: center;

    gap: 15px;

}

.banner-logo-img {

    height: 80px; /* Increased logo size */

    max-width: 100%;

}

.banner-h1 {

    font-family: "Arial Black", Gadget, sans-serif;

    font-size: 28px;

    margin: 0;

    color: white;

    max-width: 30%; /* Restrict text width to 30% */

}

/* Media query for smaller screens */

@media (max-width: 768px) {

    .banner-h1 {

        max-width: 100%; /* Full width on mobile */

    }

}

.banner-nav {

    display: none; /* Remove menu */

}

/* General app styles */

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

.risk-alert-box {

    background-color: rgba(212, 0, 44, 0.5); /* Semi-transparent red background */

    border-left: 5px solid #EF820F; /* Orange border on the left */

    padding: 20px;

    margin: 20px 0;

    border-radius: 5px;

}

.risk-alert-title {

    font-weight: bold;

    color: white;

    font-size: 18px;

    margin: 0;

    display: flex;

    align-items: center;

}

.alert-icon-circle {

    background-color: white;

    border-radius: 50%;

    width: 30px;

    height: 30px;

    display: flex;

    justify-content: center;

    align-items: center;

    margin-right: 10px;

}

/* This CSS forces the Plotly chart container to have a transparent background */

.stPlotlyChart {

    background-color: transparent !important;

}

/* New CSS rule for the page body to create margins */

main {

    padding: 0 15%;

}

</style>



<div class="main-banner">

    <div class="banner-overlay"></div>

    <div class="banner-content">

        <div class="top-header">

            <img src="https://images.learn.internationalsos.com/EloquaImages/clients/InternationalSOS/%7B0769a7db-dae2-4ced-add6-d1a73cb775d5%7D_International_SOS_white_hr_%281%29.png"

                 alt="International SOS" class="banner-logo-img">

        </div>

        <h1 class="banner-h1">Assistance and Travel Risks Simulation Report</h1>

    </div>

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



st.markdown('<div id="enter-trip-volumes"></div>', unsafe_allow_html=True)

# -------------------------

# Input Section

# -------------------------

st.markdown('<h2 style="color:#2f4696;">Enter Trip Volumes</h2>', unsafe_allow_html=True)

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

        st.markdown('<div id="estimated-needs"></div>', unsafe_allow_html=True)

        st.markdown('<h2 style="color:#2f4696;">Your Estimated Assistance Needs</h2>', unsafe_allow_html=True)

        st.write("")



        col1, col2 = st.columns([1,2])

        with col1:

            # Pluralization check for "trips"

            trip_word = "trip" if total_trips <= 1 else "trips"

            st.metric(f"Total {trip_word}", f"{total_trips:,}")

            # Pluralization check for "cases"

            case_word = "case" if total_cases < 2 else "cases"

            st.metric(f"Total Estimated {case_word}", f"{total_cases:.2f}")

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



        st.markdown('---')

        st.markdown('<div id="case-breakdown"></div>', unsafe_allow_html=True)

        # -------------------------

        # Case Type Breakdown

        # -------------------------

        col_controls_left, col_controls_right = st.columns(2)

        with col_controls_left:

            st.markdown('<h2 style="color:#2f4696;">Your Case Type Breakdown</h2>', unsafe_allow_html=True)

            filter_country = st.selectbox("Filter to one country (optional)", ["All"] + list(results_df["Country"]))

        with col_controls_right:

            st.markdown('**Benchmark against:**', unsafe_allow_html=True)

            if "benchmark_mode" not in st.session_state:

                st.session_state.benchmark_mode = "Global Average"

            

            col_btn1, col_btn2 = st.columns(2)

            

            if col_btn1.button("Global Average", key="global_btn_click", use_container_width=True):

                st.session_state.benchmark_mode = "Global Average"

            if col_btn2.button("Regional Average", key="regional_btn_click", use_container_width=True):

                st.session_state.benchmark_mode = "Regional Average"



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

            

            if st.session_state.benchmark_mode == "Global Average":

                benchmark_title = "Global Average Case Breakdown"

                case_totals_bench = data[case_columns].mean().reset_index()

                case_totals_bench.columns = ["Case Type", "Benchmark Cases"]

                case_totals_bench["Benchmark Cases"] = case_totals_bench["Benchmark Cases"] * total_trips

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



        # Pie Charts

        col_user_chart, col_bench_chart = st.columns(2)

        with col_user_chart:

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



        with col_bench_chart:

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

        

        st.markdown('---')

        st.markdown('<div id="what-it-means"></div>', unsafe_allow_html=True)

        # -------------------------

        # Recommendations Section

        # -------------------------

        st.markdown('<h2 style="color:#2f4696;">What These Results Mean for You</h2>', unsafe_allow_html=True)

        st.write("")



        # Calculate global benchmark for comparison

        global_avg_prob = data[case_columns].mean()

        global_benchmark_cases_df = (global_avg_prob * total_trips).to_frame(name="Benchmark Cases")

        global_benchmark_cases_df.index = global_benchmark_cases_df.index.str.replace(" Case Probability", "")

        

        user_case_totals_df = results_df.drop(columns=["Country", "Trips", "Total Cases"]).sum().to_frame(name="Estimated Cases")

        user_case_totals_df.index = user_case_totals_df.index.str.replace(" Case Probability", "")



        # Prepare for pluralization and dynamic content

        trip_word = "trip" if total_trips <= 1 else "trips"

        case_word = "case" if total_cases < 2 else "cases"

        countries_list_str = ', '.join(f'**{c}**' for c in countries)



        if total_cases < 1:

            st.write(f"""

            Your simulation of **{total_trips:,} {trip_word}** to **{countries_list_str}** indicates a relatively low number of estimated cases. While this is positive, it doesn’t mean the risk is zero. Even a single incident can cause significant disruption for your traveler and your business.

            """)

            st.write("")

            st.markdown("""

            This is where International SOS can still provide immense value:

            - **Proactive Risk Management:** Instead of reacting to a crisis, imagine proactively identifying and managing risks in real time. Our **Risk Information Services** and **Quantum** digital platform can monitor global threats for you, keeping your travelers ahead of potential incidents.

            - **Empowering Your Travelers:** Your travelers are your most valuable asset. What if they had **24/7 access** to on-demand medical advice from a qualified doctor or a security expert, no matter where they are? This support helps them feel confident and secure, fulfilling your **Duty of Care** responsibilities.

            - **Ensuring Business Continuity:** When an incident occurs, time is critical. Our **evacuation and repatriation services** are not just a plan; they are a rapid response network that ensures your employees can be moved quickly and safely. This minimizes disruption and protects your business.

            - **Building a Resilient Program:** Beyond a quick fix, we help you build a robust, future-proof travel risk management program. We help you align with international **guidelines** like **ISO 31030**, ensuring your program is both effective and compliant.

            """)

        else:

            st.markdown("""

            <div class="risk-alert-box">

                <p class="risk-alert-title">

                    <span class="alert-icon-circle">🚨</span> Higher Risk Alert: Your exposure is higher than the global average in the following areas:

                </p>

            </div>

            """, unsafe_allow_html=True)

            st.write("")

            

            higher_risk_messages = []

            

            user_total_cases = user_case_totals_df['Estimated Cases'].sum()

            global_total_cases = global_benchmark_cases_df['Benchmark Cases'].sum()

            

            if user_total_cases > 0 and global_total_cases > 0:

                all_higher_risks = []

                for case_type in user_case_totals_df.index:

                    user_percentage = user_case_totals_df.loc[case_type, 'Estimated Cases'] / user_total_cases

                    

                    if case_type in global_benchmark_cases_df.index:

                        global_percentage = global_benchmark_cases_df.loc[case_type, 'Benchmark Cases'] / global_total_cases

                        

                        if user_percentage > global_percentage:

                            risk_multiple = user_percentage / global_percentage

                            all_higher_risks.append({'case_type': case_type, 'risk_multiple': risk_multiple})

                

                sorted_risks = sorted(all_higher_risks, key=lambda x: x['risk_multiple'], reverse=True)

                higher_risk_messages = sorted_risks[:3]



            if higher_risk_messages:

                # Prepare a DataFrame for the horizontal bar chart

                chart_data = pd.DataFrame(higher_risk_messages)

                chart_data['risk_multiple'] = chart_data['risk_multiple'].round(1)

                

                # Create base and excess risk columns for stacked bars

                chart_data['risk_base'] = np.minimum(chart_data['risk_multiple'], 1.0)

                chart_data['risk_excess'] = np.maximum(0, chart_data['risk_multiple'] - 1.0)



                # Sort data for the chart

                chart_data = chart_data.sort_values('risk_multiple', ascending=True)



                fig = go.Figure()



                fig.add_trace(go.Bar(

                    x=chart_data['risk_base'],

                    y=chart_data['case_type'],

                    name='Global Average',

                    orientation='h',

                    marker_color='#2f4696',

                    hoverinfo='none'

                ))



                fig.add_trace(go.Bar(

                    x=chart_data['risk_excess'],

                    y=chart_data['case_type'],

                    name='Higher Risk',

                    orientation='h',

                    marker_color='#D4002C',

                    text=[f"{val:.1f}x higher" for val in chart_data['risk_multiple']],

                    textposition='outside',

                    textfont=dict(color='#D4002C', size=14, family='Arial, sans-serif')

                ))



                fig.update_layout(

                    barmode='stack',

                    title='Your Higher Risk Areas vs. Global Average',

                    title_x=0, # Left align title

                    font_color="black",

                    xaxis_title=None,

                    yaxis_title=None,

                    plot_bgcolor='rgba(0,0,0,0)',

                    paper_bgcolor='rgba(0,0,0,0)',

                    xaxis=dict(showgrid=False, range=[0, chart_data['risk_multiple'].max() * 1.1]),

                    yaxis=dict(showgrid=False, automargin=True),

                    showlegend=False,

                    width=None,

                    height=300,

                    font=dict(family='Arial, sans-serif')

                )

                

                st.plotly_chart(fig, use_container_width=True)



            else:

                st.info("Your top case types are not disproportionately higher than the global average, but proactive management is still essential.")

            

            st.markdown("""

            Based on these insights, International SOS can help you:

            - **Proactive Risk Management:** Instead of reacting to a crisis, imagine proactively identifying and managing risks in real time. Our **Risk Information Services** and **Quantum** digital platform can monitor global threats for you, keeping your travelers ahead of potential incidents.

            - **Empowering Your Travelers:** Your travelers are your most valuable asset. What if they had **24/7 access** to on-demand medical advice from a qualified doctor or a security expert, no matter where they are? This support helps them feel confident and secure, fulfilling your **Duty of Care** responsibilities.

            - **Ensuring Business Continuity:** When an incident occurs, time is critical. Our **evacuation and repatriation services** are not just a plan; they are a rapid response network that ensures your employees can be moved quickly and safely. This minimizes disruption and protects your business.

            - **Building a Resilient Program:** Beyond a quick fix, we help you build a robust, future-proof travel risk management program. We help you align with international **guidelines** like **ISO 31030**, ensuring your program is both effective and compliant.

            """)

        

        st.write("")

        st.markdown("""

        <p style="font-weight: bold;">

        These results are just the beginning. The next step is to understand how we can tailor a solution to protect your people and your business.

        </p>

        """, unsafe_allow_html=True)



        st.write("")

        st.write("")



        st.markdown('---')

        st.markdown('<div id="risk-outlook"></div>', unsafe_allow_html=True)

        # -------------------------

        # Risk Outlook section

        # -------------------------

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



st.markdown('<div id="get-in-touch"></div>', unsafe_allow_html=True)

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
