# Import of libraries
import matplotlib.pyplot as plt
import plotly as py
import pandas as pd

# Load data
recdata = pd.read_excel('KPI Team.xlsx', sheet_name='Blad1', header=1)

# Initial data exploration
recdata.info()
recdata.head(10)

# Removing erroneous rows
recdata = recdata.drop(index=[37, 38, 39, 40])

# Datetime conversion
recdata['Begin datum'] = pd.to_datetime(recdata['Begin datum'], format='%d/%m/%Y')
recdata['Eind datum'] = pd.to_datetime(recdata['Eind datum'], format='%d/%m/%Y')

# Extraction of week number
recdata['Week'] = recdata['Begin datum'].dt.isocalendar().week

# filtering and replacing nans
recdata = recdata.fillna(0)
recdata = recdata.replace('holiday', 0)

# Converting columns to appropriate data types
str_cols = ['Name']
int_cols = ['Cold call', 'Qualification', 'Introductions', 'InMails']
float_cols = ['Response rate']

# Ensure 'Name' column is converted to string
recdata['Name'] = recdata['Name'].astype('string')

for col in int_cols:
    recdata[col] = recdata[col].astype(int)

# Clean and convert 'Response rate' to float (as fraction if '%' present)
for col in float_cols:
    recdata['Response rate'] = recdata['Response rate'].astype(str).apply(
        lambda x: float(x.replace('%', '')) / 100 if '%' in x else float(x)
)
    # Calculate 'Time to hire' in days
# NOTE: Not actual 'Time to hire', likely just the employee's active worktime.
recdata['Time to hire'] = (recdata['Eind datum'] - recdata['Begin datum']).dt.days

recdata = recdata[['Name', 'Week', 'Begin datum', 'Eind datum', 'Time to hire', 'Cold call', 'InMails', 'Qualification', 'Introductions', 'Response rate']]

recdata.head()
contact = recdata['InMails'] + recdata['Cold call']

recdata['Responses (accepted or declined)'] = ((recdata['InMails'] + recdata['Cold call']) * recdata['Response rate']).round().astype(int)

recdata = recdata[['Name', 'Week', 'Begin datum', 'Eind datum', 'Time to hire', 'Cold call', 'InMails', 'Qualification', 'Introductions', 'Responses (accepted or declined)', 'Response rate']]

recdata.head()
recdata['Introductions to first contact ratio (%)'] = recdata.apply(
    lambda row: round(row['Introductions'] / (row['InMails'] + row['Cold call']) * 100, 2)
    if (row['InMails'] + row['Cold call']) > 0
    else 0,
    axis=1,
)

recdata = recdata[['Name', 'Week', 'Begin datum', 'Eind datum', 'Time to hire', 'Cold call', 'InMails', 'Qualification', 'Introductions', 'Responses (accepted or declined)', 'Response rate', 'Introductions to first contact ratio (%)']]

recdata.head()

# Based on the assumption that more than 3 introductions lead to one candidate getting through.
recdata['Candidate employment'] = recdata.apply(
    lambda row: 1 if row['Introductions'] > 3 else 0,
    axis=1,
)

recdata = recdata[['Name', 'Week', 'Begin datum', 'Eind datum', 'Time to hire', 'Cold call', 'InMails', 'Qualification', 'Introductions', 'Candidate employment', 'Responses (accepted or declined)', 'Response rate', 'Introductions to first contact ratio (%)']]

recdata.head(10)
import streamlit as st
import pandas as pd
import plotly.express as px


# Verwijder eventuele rijen zoals 'Eindtotaal'
recdata = recdata[recdata["Name"].str.lower() != "eindtotaal"]


# ===== Gemiddelden berekenen =====
avg_inmails = recdata["InMails"].mean()
avg_coldcalls = recdata["Cold call"].mean()
avg_response = recdata["Response rate"].mean()

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

    # Gemiddelde KPI's
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
            recdata,
            x="Name",
            y="InMails",
            title="InMails per Recruiter"
        )
        st.plotly_chart(fig_inmails, use_container_width=True)

    with col2:
        fig_coldcalls = px.bar(
            recdata,
            x="Name",
            y="Cold call",
            title="Cold Calls per Recruiter"
        )
        st.plotly_chart(fig_coldcalls, use_container_width=True)

    with col3:
        fig_response = px.bar(
            recdata,
            x="Name",
            y="Response rate",
            title="Response Rate per Recruiter"
        )
        st.plotly_chart(fig_response, use_container_width=True)

with tab2:
    st.header("Output KPI's")
    st.info("Hier komen later de output KPI visualisaties 🚀")