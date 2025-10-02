# ===== Import libraries =====
import streamlit as st
import pandas as pd
import plotly.express as px

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

# ===== Streamlit layout =====
st.set_page_config(page_title="Recruitment KPI Dashboard", layout="wide")
st.title("📊 Recruitment KPI Dashboard")

# Tabs
tab1, tab2 = st.tabs(["Input KPI's", "Output KPI's"])

with tab1:
    st.header("Input KPI's")

    # --- Gemiddelde KPI's per grafiek (bovenaan) ---
    col1, col2, col3, col4 = st.columns(4)  # Vier kolommen

    with col1:
        fig_avg_inmails = px.bar(
            x=["InMails"],
            y=[avg_inmails],
            text=[f"{avg_inmails:.2f}"],
            labels={"x": "KPI", "y": "Gemiddelde"},
            title="Gemiddelde InMails"
        )
        st.plotly_chart(fig_avg_inmails, use_container_width=True)

    with col2:
        fig_avg_coldcalls = px.bar(
            x=["Cold calls"],
            y=[avg_coldcalls],
            text=[f"{avg_coldcalls:.2f}"],
            labels={"x": "KPI", "y": "Gemiddelde"},
            title="Gemiddelde Cold Calls"
        )
        st.plotly_chart(fig_avg_coldcalls, use_container_width=True)

    with col3:
        fig_avg_response = px.bar(
            x=["Response rate"],
            y=[avg_response],
            text=[f"{avg_response:.2%}"],
            labels={"x": "KPI", "y": "Gemiddelde"},
            title="Gemiddelde Response Rate"
        )
        st.plotly_chart(fig_avg_response, use_container_width=True)

    with col4:
        fig_avg_qualification = px.bar(
            x=["Qualification"],
            y=[avg_qualification],
            text=[f"{avg_qualification:.2f}"],
            labels={"x": "KPI", "y": "Gemiddelde"},
            title="Gemiddelde Qualification"
        )
        st.plotly_chart(fig_avg_qualification, use_container_width=True)

    # --- Per recruiter breakdown ---
    st.subheader("Per Recruiter Breakdown")
    col1, col2, col3, col4 = st.columns(4)  # Vier kolommen

    with col1:
        fig_inmails = px.bar(recdata, x="Name", y="InMails", title="InMails per Recruiter")
        st.plotly_chart(fig_inmails, use_container_width=True)

    with col2:
        fig_coldcalls = px.bar(recdata, x="Name", y="Cold call", title="Cold Calls per Recruiter")
        st.plotly_chart(fig_coldcalls, use_container_width=True)

    with col3:
        fig_response = px.bar(recdata, x="Name", y="Response rate", title="Response Rate per Recruiter")
        st.plotly_chart(fig_response, use_container_width=True)

    with col4:
        fig_qualification = px.bar(recdata, x="Name", y="Qualification", title="Qualification per Recruiter")
        st.plotly_chart(fig_qualification, use_container_width=True)

with tab2:
    st.header("Output KPI's")
    st.info("Hier komen later de output KPI visualisaties 🚀")
