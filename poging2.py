# ===== Import libraries =====
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ===== Load data =====
recdata = pd.read_excel('KPI Team.xlsx', sheet_name='Blad1', header=1)

# ===== Data cleaning =====
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

# Verwijder eventuele totaal rijen
recdata = recdata[recdata["Name"].str.lower() != "eindtotaal"]

# ===== Gemiddelden berekenen =====
avg_inmails = recdata["InMails"].mean()
avg_coldcalls = recdata["Cold call"].mean()
avg_response = recdata["Response rate"].mean()

# Dataframe voor gemiddelde KPI's
kpi_data = pd.DataFrame({
    "KPI": ["InMails", "Cold call", "Response rate"],
    "Gemiddelde": [avg_inmails, avg_coldcalls, avg_response]
})

# ===== Streamlit layout =====
st.set_page_config(page_title="Recruitment KPI Dashboard", layout="wide")
st.title("📊 Recruitment KPI Dashboard")

# ===== Gemiddelde KPI's =====
st.subheader("Team Gemiddelde KPI's")
fig_avg = px.bar(
    kpi_data,
    x="KPI",
    y="Gemiddelde",
    text_auto=".2f",
    color="KPI",
    title="Gemiddelde KPI's per Team"
)

# Horizontale lijn als referentie (optioneel)
for i, row in kpi_data.iterrows():
    fig_avg.add_hline(y=row['Gemiddelde'], line_dash="dash", line_color="gray")

st.plotly_chart(fig_avg, use_container_width=True)

# ===== KPI's per recruiter met referentielijnen =====
st.subheader("KPI's per Recruiter")

# Functie om individuele KPI-grafiek te maken met gemiddelde lijn
def plot_kpi_per_recruiter(df, kpi, avg_value, text_format=".0f"):
    fig = px.bar(df, x="Name", y=kpi, text=text_format, title=f"{kpi} per Recruiter")
    fig.add_hline(y=avg_value, line_dash="dash", line_color="red", annotation_text="Gemiddelde", annotation_position="top left")
    fig.update_traces(textposition='outside')
    return fig

# Layout in drie kolommen
col1, col2, col3 = st.columns(3)

col1.plotly_chart(plot_kpi_per_recruiter(recdata, "InMails", avg_inmails), use_container_width=True)
col2.plotly_chart(plot_kpi_per_recruiter(recdata, "Cold call", avg_coldcalls), use_container_width=True)
col3.plotly_chart(plot_kpi_per_recruiter(recdata, "Response rate", avg_response, text_format=".2%"), use_container_width=True)
