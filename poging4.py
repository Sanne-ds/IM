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
        fig_avg_dummy = st.empty()  # Laat lege plek voor alignment
    with col4:
        fig_avg_qualification = plot_donut("Qualification", avg_qualification, targets["Qualification"], "Gemiddelde Kwalificatiecalls", color="#AB63FA")
        st.plotly_chart(fig_avg_qualification, use_container_width=True)

    # --- Gemiddelde Response Rate als eigen rij ---
    st.markdown(f"### Gemiddelde Response Rate\n**{avg_response*100:.1f}% / {targets['Response rate']*100:.0f}% doel**")

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
