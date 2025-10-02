import streamlit as st
import pandas as pd
import plotly.express as px

# ===== Data inladen =====
df = pd.read_excel("KPI Team.xlsx", header=2)  # Rij 3 bevat de kolomnamen

# Verwijder eventuele rijen zoals 'Eindtotaal'
df = df[df["Name"].str.lower() != "eindtotaal"]

# Optioneel: kolomnamen opschonen (spaties verwijderen voor gemak)
df.columns = df.columns.str.strip()

# ===== Gemiddelden berekenen =====
avg_inmails = df["InMails"].mean()
avg_coldcalls = df["Cold call"].mean()
avg_response = df["Response rate"].mean()

# Dataframe voor visualisatie van KPI's
kpi_data = pd.DataFrame({
    "KPI": ["InMails", "Cold call", "Response rate"],
    "Gemiddelde": [avg_inmails, avg_coldcalls, avg_response]
})

# ===== Streamlit Layout =====
st.set_page_config(page_title="Recruitment KPI Dashboard", layout="wide")
st.title("📊 Recruitment KPI Dashboard")

# Tabs voor Input & Output
tab1, tab2 = st.tabs(["Input KPI's", "Output KPI's"])

with tab1:
    st.header("Input KPI's")

    # Bar chart van de gemiddelden
    fig = px.bar(
        kpi_data,
        x="KPI",
        y="Gemiddelde",
        text_auto=".2f",
        title="Gemiddelde Input KPI's"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Per recruiter breakdown
    col1, col2, col3 = st.columns(3)

    with col1:
        fig_inmails = px.bar(
            df,
            x="Name",
            y="InMails",
            title="InMails per Recruiter"
        )
        st.plotly_chart(fig_inmails, use_container_width=True)

    with col2:
        fig_coldcalls = px.bar(
            df,
            x="Name",
            y="Cold call",
            title="Cold Calls per Recruiter"
        )
        st.plotly_chart(fig_coldcalls, use_container_width=True)

    with col3:
        fig_response = px.bar(
            df,
            x="Name",
            y="Response rate",
            title="Response Rate per Recruiter"
        )
        st.plotly_chart(fig_response, use_container_width=True)

with tab2:
    st.header("Output KPI's")
    st.info("Hier komen later de output KPI visualisaties 🚀")
