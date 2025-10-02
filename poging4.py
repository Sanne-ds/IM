# ===== Import libraries =====
import streamlit as st
import pandas as pd
import plotly.express as px

# ===== Load & preprocess data =====
try:
    recdata = pd.read_excel('KPI Team.xlsx', sheet_name='Blad1', header=1)
except FileNotFoundError:
    st.error("Bestand 'KPI Team.xlsx' niet gevonden. Zorg ervoor dat het bestand in de juiste map staat.")
    st.stop()

# Remove erroneous rows safely
recdata = recdata.drop(index=[37, 38, 39, 40], errors='ignore')

# Datetime conversion
recdata['Begin datum'] = pd.to_datetime(recdata['Begin datum'], format='%d/%m/%Y', errors='coerce')
recdata['Eind datum'] = pd.to_datetime(recdata['Eind datum'], format='%d/%m/%Y', errors='coerce')

# Extract week number
if 'Begin datum' in recdata.columns and not recdata['Begin datum'].isnull().all():
    recdata['Week'] = recdata['Begin datum'].dt.isocalendar().week
else:
    recdata['Week'] = 0

# Fill NaNs and replace 'holiday' entries
recdata = recdata.fillna(0)
recdata = recdata.replace('holiday', 0)

# Convert columns to proper types
recdata['Name'] = recdata['Name'].astype(str)
for col in ['Cold call', 'Qualification', 'Introductions', 'InMails']:
    recdata[col] = recdata[col].astype(int)

recdata['Response rate'] = recdata['Response rate'].astype(str).apply(
    lambda x: float(x.replace('%', '')) / 100 if '%' in x else float(x)
)

# Calculate additional metrics
recdata['Time to hire'] = (recdata['Eind datum'] - recdata['Begin datum']).dt.days
recdata['Responses (accepted or declined)'] = ((recdata['InMails'] + recdata['Cold call']) * recdata['Response rate']).round().astype(int)
recdata['Introductions to first contact ratio (%)'] = recdata.apply(
    lambda row: round(row['Introductions'] / (row['InMails'] + row['Cold call']) * 100, 2)
    if (row['InMails'] + row['Cold call']) > 0 else 0, axis=1
)
recdata['Candidate employment'] = recdata['Introductions'].apply(lambda x: 1 if x > 3 else 0)

# Remove "Eindtotaal" row
recdata = recdata[recdata["Name"].str.lower() != "eindtotaal"]

# ===== Calculate averages =====
avg_inmails = recdata["InMails"].mean()
avg_coldcalls = recdata["Cold call"].mean()
avg_response = recdata["Response rate"].mean()
avg_qualification = recdata["Qualification"].mean()

# ===== Define targets =====
targets = {
    "InMails": 150,
    "Cold call": 20,
    "Response rate": 0.25,  # fraction
    "Qualification": 15
}

# ===== Define fixed colors per KPI =====
kpi_colors = {
    "InMails": "#636EFA",
    "Cold call": "#EF553B",
    "Response rate": "#00CC96",
    "Qualification": "#AB63FA"
}

# ===== Functie die ervoor zorgt dat behaald resultaat kleur heeft en onbehaald grijs =====
def plot_donut(kpi_name, avg_value, target, title):
    """
    kpi_name: str, naam van de KPI
    avg_value: float, behaalde waarde
    target: float, doelwaarde
    title: str, titel van de grafiek
    """
    # Behaald en nog te behalen
    achieved = min(avg_value, target)
    remaining = max(target - avg_value, 0)

    # DataFrame: behaalde waarde altijd eerst
    df = pd.DataFrame({
        "Categorie": [kpi_name, "Nog te behalen"],
        "Waarde": [achieved, remaining]
    })

    # Kleur ophalen uit vaste kleurenlijst
    color = kpi_colors.get(kpi_name)

    # Maak de donut chart
    fig = px.pie(
        df,
        names="Categorie",
        values="Waarde",
        hole=0.5,
        title=title,
        color="Categorie",
        color_discrete_map={
            kpi_name: color,
            "Nog te behalen": "#E5ECF6"
        }
    )

    fig.update_layout(showlegend=False, title_x=0.5)
    
    # Alleen percentage tonen, geen label
    fig.update_traces(textinfo='percent', textfont_size=14, sort=False, direction='clockwise', rotation=90)

    return fig

# ===== Streamlit layout =====
st.set_page_config(page_title="Recruitment KPI Dashboard", layout="wide")
st.title("📊 Recruitment KPI Dashboard")

# Tabs
tab1, tab2 = st.tabs(["Input KPI's", "Output KPI's"])

with tab1:
    st.header("Input KPI's")

    st.subheader("Gemiddelde Resultaten t.o.v. Doel")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        fig_avg_inmails = plot_donut("InMails", avg_inmails, targets["InMails"], "Gemiddelde InMails")
        st.plotly_chart(fig_avg_inmails, use_container_width=True)

    with col2:
        fig_avg_coldcalls = plot_donut("Cold call", avg_coldcalls, targets["Cold call"], "Gemiddelde Cold Calls")
        st.plotly_chart(fig_avg_coldcalls, use_container_width=True)

    with col3:
        fig_avg_response = plot_donut("Response rate", avg_response, targets["Response rate"], "Gemiddelde Response Rate")
        st.plotly_chart(fig_avg_response, use_container_width=True)

    with col4:
        fig_avg_qualification = plot_donut("Qualification", avg_qualification, targets["Qualification"], "Gemiddelde Kwalificatiecalls")
        st.plotly_chart(fig_avg_qualification, use_container_width=True)

    st.divider()
    
    st.subheader("Resultaten per Recruiter")
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        fig_inmails = px.bar(recdata, x="Name", y="InMails", title="InMails per Recruiter", color_discrete_sequence=[kpi_colors["InMails"]])
        st.plotly_chart(fig_inmails, use_container_width=True)

    with col6:
        fig_coldcalls = px.bar(recdata, x="Name", y="Cold call", title="Cold Calls per Recruiter", color_discrete_sequence=[kpi_colors["Cold call"]])
        st.plotly_chart(fig_coldcalls, use_container_width=True)

    with col7:
        fig_response = px.bar(recdata, x="Name", y="Response rate", title="Response Rate per Recruiter", color_discrete_sequence=[kpi_colors["Response rate"]])
        st.plotly_chart(fig_response, use_container_width=True)

    with col8:
        fig_qualification = px.bar(recdata, x="Name", y="Qualification", title="Kwalificatiecalls per Recruiter", color_discrete_sequence=[kpi_colors["Qualification"]])
        st.plotly_chart(fig_qualification, use_container_width=True)

with tab2:
    st.header("Output KPI's")
    st.info("Hier komen later de output KPI visualisaties 🚀")
