import streamlit as st
import pandas as pd
import plotly.express as px
from analytics_engine import LogisticsAnalytics

st.set_page_config(
    page_title="Real-Time Logistics Bottleneck Monitor",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Real-Time Logistics Bottleneck Monitor")
st.markdown(
    "Upload shipment CSV and get bottleneck detection, financial impact analysis, and optimization insights."
)

uploaded_file = st.file_uploader(
    "Upload Shipment CSV",
    type=["csv"]
)

if uploaded_file is not None:

    temp_file = "uploaded_shipments.csv"

    with open(temp_file, "wb") as f:
        f.write(uploaded_file.getbuffer())

    analytics = LogisticsAnalytics(temp_file)

    st.success("CSV Uploaded Successfully")

    df = analytics.df

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    if st.button("Run Analytics"):

        progress = st.progress(0)

        # ---------- Run Analysis ----------
        progress.progress(20)
        delay_region = analytics.calculate_delay_by_region()

        progress.progress(40)
        financial_loss = analytics.calculate_financial_loss_hourly()

        progress.progress(60)
        bottlenecks = analytics.identify_bottlenecks()

        progress.progress(80)
        trends = analytics.trend_analysis()

        progress.progress(100)
        opportunities = analytics.cost_optimization_opportunities()

        st.success("Analysis Complete")

        # ---------- KPI Cards ----------
        st.subheader("Business KPIs")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Shipments",
            f"{len(df):,}"
        )

        delayed_shipments = len(
            df[df["Status"].isin(["Delayed", "Critical Delay"])]
        )

        col2.metric(
            "Delayed Shipments",
            f"{delayed_shipments:,}"
        )

        col3.metric(
            "Total Financial Loss",
            f"${df['Financial_Loss_USD'].sum():,.0f}"
        )

        col4.metric(
            "Average Delay",
            f"{df['Delay_Hours'].mean():.1f} hrs"
        )

        # ---------- Tabs ----------
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Regional Analysis",
            "Carrier Analysis",
            "Bottlenecks",
            "Trend Analysis",
            "Optimization Insights"
        ])

        # ---------- Regional ----------
        with tab1:

            st.subheader("Regional Delay Analysis")

            st.dataframe(delay_region)

            fig_region = px.bar(
                delay_region.reset_index(),
                x="Region",
                y="Avg_Delay",
                title="Average Delay by Region"
            )

            st.plotly_chart(
                fig_region,
                use_container_width=True
            )

        # ---------- Carrier ----------
        with tab2:

            st.subheader("Carrier Performance")

            carrier_df = (
                financial_loss["by_carrier"]
                .head(10)
                .reset_index()
            )

            st.dataframe(carrier_df)

            fig_carrier = px.bar(
                carrier_df,
                x="Carrier",
                y="Total_Loss_USD",
                title="Financial Loss by Carrier"
            )

            st.plotly_chart(
                fig_carrier,
                use_container_width=True
            )

        # ---------- Bottlenecks ----------
        with tab3:

            st.subheader("Top Bottleneck Routes")

            top_routes = (
                bottlenecks
                .head(10)
                .reset_index()
            )

            st.dataframe(top_routes)

            fig_routes = px.bar(
                top_routes,
                x="Route",
                y="Total_Loss",
                title="Top Loss-Making Routes"
            )

            st.plotly_chart(
                fig_routes,
                use_container_width=True
            )

        # ---------- Trends ----------
        with tab4:

            st.subheader("Delay Trends")

            trend_df = trends.reset_index()

            st.dataframe(trend_df)

            fig_trend = px.line(
                trend_df,
                x="Date",
                y="Avg_Delay_Hours",
                title="Average Delay Trend"
            )

            st.plotly_chart(
                fig_trend,
                use_container_width=True
            )

        # ---------- Insights ----------
        with tab5:

            st.subheader("Optimization Opportunities")

            st.metric(
                "Total Financial Loss",
                f"${opportunities['total_loss']:,.0f}"
            )

            st.metric(
                "10% Savings Target",
                f"${opportunities['target_savings']:,.0f}"
            )

            st.metric(
                "Potential Opportunity Value",
                f"${opportunities['opportunity_sum']:,.0f}"
            )

        # ---------- Downloads ----------
        st.subheader("Download Reports")

        st.download_button(
            "Download Regional Analytics CSV",
            delay_region.to_csv(index=True),
            file_name="regional_analysis.csv",
            mime="text/csv"
        )

        st.download_button(
            "Download Bottleneck Routes CSV",
            bottlenecks.to_csv(index=True),
            file_name="bottlenecks.csv",
            mime="text/csv"
        )