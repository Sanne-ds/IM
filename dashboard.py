import streamlit as st
import pandas as pd
import plotly.express as px

# ===== Data inladen =====
df = pd.read_excel("KPI Team.xlsx", header=2)  # Rij 3 bevat de kolomnamen

# Verwijder eventuele rijen zoals 'Eindtotaal'
df = df[df["Name"].str.lower() != "eindtotaal"]

# Kolomnamen opschonen
df.columns = df.columns.str.strip().str.lower()

# Mapping van kolommen
col_name_map = {
    "name": "name",
    "inmails": "som van inmails",
    "coldcalls": "cold call",
    "response": "gemiddelde van response rate"
}

# ===== Gemiddelden berekenen =====
avg_inmails = df[col_name_map["inmails"]].mean()
avg_coldcalls = df[col_name_map["coldcalls"]].mean()
avg_response = df[col_name_map["response"]].mean()

# Voor visualisaties: een dataframe met de KPI's
kpi_data = pd.DataFrame({
    "KPI": ["Inmails", "Cold calls", "Response rate"],
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
            x=col_name_map["name"],
            y=col_name_map["inmails"],
            title="Inmails per Recruiter"
        )
        st.plotly_chart(fig_inmails, use_container_width=True)

    with col2:
        fig_coldcalls = px.bar(
            df,
            x=col_name_map["name"],
            y=col_name_map["coldcalls"],
            title="Cold Calls per Recruiter"
        )
        st.plotly_chart(fig_coldcalls, use_container_width=True)

    with col3:
        fig_response = px.bar(
            df,
            x=col_name_map["name"],
            y=col_name_map["response"],
            title="Response Rate per Recruiter"
        )
        st.plotly_chart(fig_response, use_container_width=True)

with tab2:
    st.header("Output KPI's")
    st.info("Hier komen later de output KPI visualisaties 🚀")
