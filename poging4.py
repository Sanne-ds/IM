# ===== Import libraries =====
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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

# ===== Calculate averages =====
avg_inmails = recdata["InMails"].mean()
avg_coldcalls = recdata["Cold call"].mean()
avg_response = recdata["Response rate"].mean()
avg_qualification = recdata["Qualification"].mean()

# ===== Define targets =====
targets = {
    "InMails": 150,
    "Cold call": 20,
    "Response rate": 0.25,
    "Qualification": 15
}

# ===== Donut chart function =====
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
    fig.update_traces(textinfo='none', sort=False)
    fig.add_annotation(
        text=f"{percent_achieved:.0f}%",
        x=0.5, y=0.5,
        font_size=28,
        showarrow=False
    )
    fig.update_layout(title_text=title, margin=dict(t=40, b=0, l=0, r=0))
    return fig

# ===== Response rate progress bar =====
def plot_response_rate_bar(avg_value, target):
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
        title=dict(text="Gemiddelde Response Rate", x=0.5, xanchor='center', yanchor='top')
    )
    return fig

# ===== Color mapping for recruiters =====
recruiters = recdata['Name'].unique()
colors = px.colors.qualitative.Set3
colors = (colors * ((len(recruiters)//len(colors))+1))[:len(recruiters)]
color_map = dict(zip(recruiters, colors))

# ===== Function to create individual bar chart with target =====
def bar_chart_with_target(y_values, y_max, target, title):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=recdata['Name'],
        y=y_values,
        marker_color=[color_map[name] for name in recdata['Name']]
    ))
    fig.update_layout(
        yaxis=dict(range=[0, y_max]),
        title=title,
        height=300
    )
    fig.add_hline(y=target, line_dash="dash", line_color="red", line_width=3)
    return fig

# ===== Streamlit layout =====
st.set_page_config(page_title="Recruitment KPI Dashboard", layout="wide")
st.title("📊 Recruitment KPI Dashboard")

tab1, tab2 = st.tabs(["Input KPI's", "Output KPI's"])

with tab1:
    st.header("Input KPI's")

    # --- Donut charts ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(plot_donut("InMails", avg_inmails, targets["InMails"], "Gemiddelde InMails", color="#636EFA"), use_container_width=True)
    with col2:
        st.plotly_chart(plot_donut("Cold Calls", avg_coldcalls, targets["Cold call"], "Gemiddelde Cold Calls", color="#EF553B"), use_container_width=True)
    with col3:
        st.plotly_chart(plot_donut("Qualification", avg_qualification, targets["Qualification"], "Gemiddelde Kwalificatiecalls", color="#AB63FA"), use_container_width=True)

    # --- Response Rate progress bar ---
    st.plotly_chart(plot_response_rate_bar(avg_response, targets['Response rate']), use_container_width=True)

    # --- Per recruiter breakdown ---
    st.subheader("Per Recruiter Breakdown")
    col1, col2, col3, col4 = st.columns(4)

    # InMails
    with col1:
        fig_inmails = bar_chart_with_target(recdata['InMails'], y_max=200, target=100, title="InMails per Recruiter")
        st.plotly_chart(fig_inmails, use_container_width=True)

    # Cold Calls
    with col2:
        fig_coldcalls = bar_chart_with_target(recdata['Cold call'], y_max=100, target=20, title="Cold Calls per Recruiter")
        st.plotly_chart(fig_coldcalls, use_container_width=True)

    # Response Rate
    with col3:
        fig_response = bar_chart_with_target(recdata['Response rate']*100, y_max=100, target=25, title="Response Rate per Recruiter")
        st.plotly_chart(fig_response, use_container_width=True)

    # Qualification
    with col4:
        fig_qualification = bar_chart_with_target(recdata['Qualification'], y_max=30, target=15, title="Qualification per Recruiter")
        st.plotly_chart(fig_qualification, use_container_width=True)

with tab2:
    st.header("Output KPI's")
    st.info("Hier komen later de output KPI visualisaties 🚀")
