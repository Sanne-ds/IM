import streamlit as st
import pandas as pd
import plotly.express as px

# Verwijder eventuele rijen zoals 'Eindtotaal'
recdata = recdata[recdata["Name"].str.lower() != "eindtotaal"]

# ===== Gemiddelden berekenen =====
avg_inmails = recdata["InMails"].mean()
avg_coldcalls = recdata["Cold call"].mean()
avg_response = recdata["Response rate"].mean()

# ===== Streamlit Layout =====
st.set_page_config(page_title="Recruitment KPI Dashboard", layout="wide")
st.title("📊 Recruitment KPI Dashboard")

# Tabs voor Input & Output
tab1, tab2 = st.tabs(["Input KPI's", "Output KPI's"])

with tab1:
    st.header("Input KPI's")

    # --- Gemiddelde KPI's per grafiek ---
    col1, col2, col3 = st.columns(3)

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

    # --- Per recruiter breakdown ---
    st.subheader("Per Recruiter Breakdown")
    col1, col2, col3 = st.columns(3)
    with col1:
        fig_inmails = px.bar(recdata, x="Name", y="InMails", title="InMails per Recruiter")
        st.plotly_chart(fig_inmails, use_container_width=True)
    with col2:
        fig_coldcalls = px.bar(recdata, x="Name", y="Cold call", title="Cold Calls per Recruiter")
        st.plotly_chart(fig_coldcalls, use_container_width=True)
    with col3:
        fig_response = px.bar(recdata, x="Name", y="Response rate", title="Response Rate per Recruiter")
        st.plotly_chart(fig_response, use_container_width=True)

with tab2:
    st.header("Output KPI's")
    st.info("Hier komen later de output KPI visualisaties 🚀")
