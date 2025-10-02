# ===== Import libraries =====
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ===== Load & preprocess data =====
recdata = pd.read_excel('KPI Team.xlsx', sheet_name='Blad1', header=1)

# Remove erroneous rows safely
recdata = recdata.drop(index=[37, 38, 39, 40], errors='ignore')

# Datetime conversion
recdata['Begin datum'] = pd.to_datetime(recdata['Begin datum'], format='%d/%m/%Y', errors='coerce')
recdata['Eind datum'] = pd.to_datetime(recdata['Eind datum'], format='%d/%m/%Y', errors='coerce')

# Extract week number
recdata['Week'] = recdata['Begin datum'].dt.isocalendar().week

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

# ===== Function to create donut chart with consistent colors =====
def plot_donut(kpi_name, avg_value, target, title, color="#636EFA"):
    remaining = max(target - avg_value, 0)
    fig = px.pie(
        names=[kpi_name, "Nog te behalen"],
        values=[avg_value, remaining],
        hole=0.5,
        color_discrete_sequence=[color, "#E5ECF6"],  # Grijs voor niet behaalde
    )
    fig.update_traces(textinfo='percent+label')
    fig.update_layout(title_text=title)
    return fig

# ===== Function to create per-recruiter stacked bar chart =====
def plot_kpi_per_recruiter(df, kpi_col, target, title, color):
    remaining = df[kpi_col].apply(lambda x: max(target - x, 0))
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Name"],
        y=df[kpi_col],
        name=kpi_col,
        marker_color=color
    ))
    fig.add_trace(go.Bar(
        x=df["Name"],
        y=remaining,
        name="Nog te behalen",
        marker_color="#E5ECF6"
    ))
    fig.update_layout(
        barmode='stack',
        title=title,
        yaxis=dict(title=kpi_col)
    )
    return fig

# ===== Streamlit layout =====
st.set_page_config(page_title="Recruitment KPI Dashboard", layout="wide")
st.title("📊 Recruitment KPI Dashboard")

# Tabs
tab1, tab2 = st.tabs(["Input KPI's", "Output KPI's"])

with tab1:
    st.header("Input KPI's")

    # --- Gemiddelde KPI's als donut charts ---
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        fig_avg_inmails = plot_donut("InMails", avg_inmails, targets["InMails"], "Gemiddelde InMails", color="#636EFA")
        st.plotly_chart(fig_avg_inmails, use_container_width=True)

    with col2:
        fig_avg_coldcalls = plot_donut("Cold Calls", avg_coldcalls, targets["Cold call"], "Gemiddelde Cold Calls", color="#EF553B")
        st.plotly_chart(fig_avg_coldcalls, use_container_width=True)

    with col3:
        fig_avg_response = plot_donut("Response Rate", avg_response, targets["Response rate"], "Gemiddelde Response Rate", color="#00CC96")
        st.plotly_chart(fig_avg_response, use_container_width=True)

    with col4:
        fig_avg_qualification = plot_donut("Qualification", avg_qualification, targets["Qualification"], "Gemiddelde Kwalificatiecalls", color="#AB63FA")
        st.plotly_chart(fig_avg_qualification, use_container_width=True)

    # --- Per recruiter breakdown ---
    st.subheader("Per Recruiter Breakdown")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        fig_inmails = plot_kpi_per_recruiter(recdata, "InMails", targets["InMails"], "InMails per Recruiter", "#636EFA")
        st.plotly_chart(fig_inmails, use_container_width=True)

    with col2:
        fig_coldcalls = plot_kpi_per_recruiter(recdata, "Cold call", targets["Cold call"], "Cold Calls per Recruiter", "#EF553B")
        st.plotly_chart(fig_coldcalls, use_container_width=True)

    with col3:
        fig_response = plot_kpi_per_recruiter(recdata, "Response rate", targets["Response rate"], "Response Rate per Recruiter", "#00CC96")
        st.plotly_chart(fig_response, use_container_width=True)

    with col4:
        fig_qualification = plot_kpi_per_recruiter(recdata, "Qualification", targets["Qualification"], "Qualification per Recruiter", "#AB63FA")
        st.plotly_chart(fig_qualification, use_container_width=True)

with tab2:
    st.header("Output KPI's")
    st.info("Hier komen later de output KPI visualisaties 🚀")
