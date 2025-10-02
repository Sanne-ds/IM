import streamlit as st
import pandas as pd
import plotly.express as px

# ===== Load en clean data =====
recdata = pd.read_excel('KPI Team.xlsx', sheet_name='Blad1', header=1)
recdata = recdata.drop(index=[37, 38, 39, 40])
recdata['Begin datum'] = pd.to_datetime(recdata['Begin datum'], format='%d/%m/%Y')
recdata['Eind datum'] = pd.to_datetime(recdata['Eind datum'], format='%d/%m/%Y')
recdata['Week'] = recdata['Begin datum'].dt.isocalendar().week
recdata = recdata.fillna(0).replace('holiday', 0)
recdata['Name'] = recdata['Name'].astype(str)

int_cols = ['Cold call', 'Qualification', 'Introductions', 'InMails']
float_cols = ['Response rate']

for col in int_cols:
    recdata[col] = recdata[col].astype(int)

for col in float_cols:
    recdata['Response rate'] = recdata['Response rate'].astype(str).apply(
        lambda x: float(x.replace('%',''))/100 if '%' in x else float(x)
    )

recdata['Time to hire'] = (recdata['Eind datum'] - recdata['Begin datum']).dt.days
recdata['Responses (accepted or declined)'] = ((recdata['InMails'] + recdata['Cold call']) * recdata['Response rate']).round().astype(int)
recdata['Introductions to first contact ratio (%)'] = recdata.apply(
    lambda row: round(row['Introductions'] / (row['InMails'] + row['Cold call']) * 100,2)
    if (row['InMails'] + row['Cold call'])>0 else 0,
    axis=1
)
recdata['Candidate employment'] = recdata.apply(lambda row: 1 if row['Introductions']>3 else 0, axis=1)

recdata = recdata[recdata["Name"].str.lower() != "eindtotaal"]

# ===== Gemiddelden =====
avg_inmails = recdata["InMails"].mean()
avg_coldcalls = recdata["Cold call"].mean()
avg_response = recdata["Response rate"].mean()

kpi_data = pd.DataFrame({
    "KPI": ["InMails", "Cold call", "Response rate"],
    "Gemiddelde": [avg_inmails, avg_coldcalls, avg_response]
})

# ===== Streamlit layout =====
st.set_page_config(page_title="Recruitment KPI Dashboard", layout="wide")
st.title("📊 Recruitment KPI Dashboard")

# ===== Gemiddelde KPI's =====
st.subheader("Gemiddelde KPI's per Team")
fig_avg = px.bar(
    kpi_data,
    x="KPI",
    y="Gemiddelde",
    text_auto=".2f",
    title="Team Gemiddelde KPI's"
)
st.plotly_chart(fig_avg, use_container_width=True)

# ===== Individuele recruiter grafieken =====
st.subheader("KPI's per Recruiter")
col1, col2, col3 = st.columns(3)

with col1:
    fig_inmails = px.bar(
        recdata,
        x="Name",
        y="InMails",
        title="InMails per Recruiter",
        text_auto=True
    )
    st.plotly_chart(fig_inmails, use_container_width=True)

with col2:
    fig_coldcalls = px.bar(
        recdata,
        x="Name",
        y="Cold call",
        title="Cold Calls per Recruiter",
        text_auto=True
    )
    st.plotly_chart(fig_coldcalls, use_container_width=True)

with col3:
    fig_response = px.bar(
        recdata,
        x="Name",
        y="Response rate",
        title="Response Rate per Recruiter",
        text_auto=".2%",
    )
    st.plotly_chart(fig_response, use_container_width=True)
