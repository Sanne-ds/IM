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
    values = [min(avg_value, target), remaining]
    
    fig = px.pie(
        names=[kpi_name, "Nog te behalen"],
        values=values,
        hole=0.5,
        color_discrete_sequence=[color, "#E5ECF6"],  # Grijs voor niet behaalde
    )
    
    fig.update_traces(textinfo='percent+label', sort=False)
    fig.update_layout(title_text=title)
    
    return fig

# ===== Function to create response rate progress bar =====
def plot_response_rate_bar(avg_value, target):
    """
    avg_value: huidige gemiddelde response rate (0-1)
    target: target value (0-1)
    """
    fig = go.Figure()

    # Huidige waarde
    fig.add_trace(go.Bar(
        x=[avg_value*100],
        y=["Response Rate"],
        orientation='h',
        marker=dict(color="#00CC96"),
        width=0.5,
        name="Huidige waarde"
    ))

    # Target als verticale lijn
    fig.add_shape(
        type="line",
        x0=target*100, x1=target*100,
        y0=-0.5, y1=0.5,
        line=dict(color="red", width=4, dash="dash"),
        xref="x", yref="y"
    )

    # Layout
    fig.update_layout(
        xaxis=dict(range=[0,100], title="Percentage (%)"),
        yaxis=dict(showticklabels=False),
        showlegend=False,
        height=100,
        margin=dict(l=20, r=20, t=20, b=20),
        title="Gemiddelde Response Rate"
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
        st.empty()  # lege kolom voor alignment
    with col4:
        fig_avg_qualification = plot_donut("Qualification", avg_qualification, targets["Qualification"], "Gemiddelde Kwalificatiecalls", color="#AB63FA")
        st.plotly_chart(fig_avg_qualification, use_container_width=True)

    # --- Gemiddelde Response Rate progressbar in eigen rij ---
    fig_avg_response_bar = plot_response_rate_bar(avg_response, targets['Response rate'])
    st.plotly_chart(fig_avg_response_bar, use_container_width=True)

    # --- Per recruiter breakdown ---
    st.subheader("Per Recruiter Breakdown")
    col1, col2, col3, col4 = st.columns(4)
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
