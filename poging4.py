# ===== Import libraries =====
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ===== Load & preprocess data =====
recdata = pd.read_excel('KPI Team.xlsx', sheet_name='Blad1', header=1)
recdata = recdata.drop(index=[37, 38, 39, 40], errors='ignore')
recdata['Begin datum'] = pd.to_datetime(recdata['Begin datum'], format='%d/%m/%Y', errors='coerce')
recdata['Eind datum'] = pd.to_datetime(recdata['Eind datum'], format='%d/%m/%Y', errors='coerce')
recdata['Week'] = recdata['Begin datum'].dt.isocalendar().week
recdata = recdata.fillna(0)
recdata = recdata.replace('holiday', 0)

recdata['Name'] = recdata['Name'].astype(str)
for col in ['Cold call', 'Qualification', 'Introductions', 'InMails']:
    recdata[col] = recdata[col].astype(int)
recdata['Response rate'] = recdata['Response rate'].astype(str).apply(
    lambda x: float(x.replace('%', '')) / 100 if '%' in x else float(x)
)

recdata['Time to hire'] = (recdata['Eind datum'] - recdata['Begin datum']).dt.days
recdata['Responses (accepted or declined)'] = ((recdata['InMails'] + recdata['Cold call']) * recdata['Response rate']).round().astype(int)
recdata['Introductions to first contact ratio (%)'] = recdata.apply(
    lambda row: round(row['Introductions'] / (row['InMails'] + row['Cold call']) * 100, 2)
    if (row['InMails'] + row['Cold call']) > 0 else 0, axis=1
)
recdata['Candidate employment'] = recdata['Introductions'].apply(lambda x: 1 if x > 3 else 0)
recdata = recdata[recdata["Name"].str.lower() != "eindtotaal"]

# ===== Week filter (dropdown menu) =====
week_options = ['Afgelopen maand'] + sorted(recdata['Week'].unique().tolist())
selected_week = st.selectbox("Selecteer week", week_options)  # dropdown menu

# Filter de data op geselecteerde week of afgelopen maand
if selected_week != 'Afgelopen maand':
    filtered_data = recdata[recdata['Week'] == int(selected_week)]
    week_label = f"Week {selected_week}"
    multiplier = 1  # streefwaarden normaal
else:
    # Neem de laatste 4 weken
    last_weeks = sorted(recdata['Week'].unique())[-4:]
    filtered_data = recdata[recdata['Week'].isin(last_weeks)]
    week_label = "Afgelopen maand"
    multiplier = 4  # streefwaarden maal 4

# ===== Define targets =====
targets = {
    "InMails": 150 * multiplier,
    "Cold call": 20 * multiplier,
    "Response rate": 0.25,  # percentage blijft gelijk
    "Qualification": 15 * multiplier
}

# ===== Calculate averages =====
avg_inmails = filtered_data["InMails"].mean()
avg_coldcalls = filtered_data["Cold call"].mean()
avg_response = filtered_data["Response rate"].mean()
avg_qualification = filtered_data["Qualification"].mean()

# ===== Function to create donut chart with central percentage =====
def plot_donut(kpi_name, avg_value, target, title, color="#636EFA"):
    remaining = max(target - avg_value, 0)
    values = [min(avg_value, target), remaining]

    percent_achieved = min(avg_value / target * 100, 100) if target > 0 else 0

    fig = px.pie(
        names=[kpi_name, "Nog te behalen"],
        values=values,
        hole=0.5,
        color_discrete_sequence=[color, "#E5ECF6"],
        height=300
    )

    # Verwijder labels van segmenten
    fig.update_traces(textinfo='none', sort=False)

    # Voeg percentage in het midden toe
    fig.add_annotation(
        text=f"{percent_achieved:.0f}%",
        x=0.5, y=0.5,
        font_size=28,
        showarrow=False
    )

    fig.update_layout(
        title_text=title,
        margin=dict(t=40, b=0, l=0, r=0)
    )

    return fig

# ===== Function to create response rate progress bar =====
def plot_response_rate_bar(avg_value, target, title):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[avg_value*100],
        y=[""],
        orientation='h',
        marker=dict(color="#00CC96"),
        width=0.6
    ))

    fig.add_shape(
        type="line",
        x0=target*100, x1=target*100,
        y0=-0.5, y1=0.5,
        line=dict(color="red", width=4, dash="dash"),
        xref="x", yref="y"
    )

    fig.update_layout(
        xaxis=dict(range=[0,100], title="Percentage (%)"),
        yaxis=dict(showticklabels=False),
        showlegend=False,
        height=150,
        margin=dict(l=20, r=20, t=60, b=20),
        title=dict(text=title, x=0.5, xanchor='center', yanchor='top')
    )

    return fig

# ===== Streamlit layout =====
st.set_page_config(page_title="Recruitment KPI Dashboard", layout="wide")
st.title("📊 Recruitment KPI Dashboard")

tab1, tab2 = st.tabs(["Input KPI's", "Output KPI's"])

with tab1:
    st.header("Input KPI's")

    # --- Gemiddelde KPI's als donut charts in 3 kolommen ---
    col1, col2, col3 = st.columns(3)
    with col1:
        fig_avg_inmails = plot_donut("InMails", avg_inmails, targets["InMails"], f"Gemiddelde InMails ({week_label})", color="#636EFA")
        st.plotly_chart(fig_avg_inmails, use_container_width=True)
    with col2:
        fig_avg_coldcalls = plot_donut("Cold Calls", avg_coldcalls, targets["Cold call"], f"Gemiddelde Cold Calls ({week_label})", color="#EF553B")
        st.plotly_chart(fig_avg_coldcalls, use_container_width=True)
    with col3:
        fig_avg_qualification = plot_donut("Qualification", avg_qualification, targets["Qualification"], f"Gemiddelde Kwalificatiecalls ({week_label})", color="#AB63FA")
        st.plotly_chart(fig_avg_qualification, use_container_width=True)

    # --- Gemiddelde Response Rate progressbar in eigen rij ---
    fig_avg_response_bar = plot_response_rate_bar(avg_response, targets['Response rate'], f"Gemiddelde Response Rate ({week_label})")
    st.plotly_chart(fig_avg_response_bar, use_container_width=True)

    # --- Per recruiter breakdown ---
    st.subheader(f"Per Recruiter Breakdown ({week_label})")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        fig_inmails = px.bar(filtered_data, x="Name", y="InMails", title="InMails per Recruiter", height=300)
        st.plotly_chart(fig_inmails, use_container_width=True)
    with col2:
        fig_coldcalls = px.bar(filtered_data, x="Name", y="Cold call", title="Cold Calls per Recruiter", height=300)
        st.plotly_chart(fig_coldcalls, use_container_width=True)
    with col3:
        fig_response = px.bar(filtered_data, x="Name", y="Response rate", title="Response Rate per Recruiter", height=300)
        st.plotly_chart(fig_response, use_container_width=True)
    with col4:
        fig_qualification = px.bar(filtered_data, x="Name", y="Qualification", title="Qualification per Recruiter", height=300)
        st.plotly_chart(fig_qualification, use_container_width=True)

with tab2:
    st.header("Output KPI's")
    st.info("Hier komen later de output KPI visualisaties 🚀")
