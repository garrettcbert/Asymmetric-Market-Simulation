import streamlit as st
import pandas as pd
import plotly.express as px
from math import floor

from src.pages.glossary import expander as glossary_expander


def render():
    st.title("Full Data View")
    st.markdown("Compare the outcomes of different simulation setups.")
    glossary_expander()

    if "round_stats" not in st.session_state:
        st.warning("Run the simulation first to view the data.")
        return

    round_stats = st.session_state.round_stats
    if not round_stats:
        st.warning("No simulation data available.")
        return

    round_tabs = st.tabs([f"Round {r['round']}" for r in round_stats])
    for tab, r in zip(round_tabs, round_stats):
        with tab:
            st.subheader(f"Round {r['round']} Data")
            st.dataframe(r['dataframe'])
            st.markdown(f"**Market Price:** ${r['market_price']}")
            st.markdown(f"**Average Quality:** {r['avg_quality']:.2f}")
            st.markdown(f"**Sellers Remaining:** {r['num_sales']}")
            st.markdown(f"**Total Seller Surplus:** ${floor(r['seller surplus'].sum())}")
            st.markdown(f"**Total Buyer Surplus:** ${floor(r['buyer surplus'].sum())}")
            st.markdown(f"**Total Surplus:** ${floor(r['seller surplus'].sum() + r['buyer surplus'].sum())}")
            st.plotly_chart(r['quality_plot'], use_container_width=True)
            st.plotly_chart(r['surplus_plot'], use_container_width=True)
            st.markdown(f"**Government Cost:** ${floor(r['gov cost'])}")

    big_metrics = {
        'Market Price': [r['market_price'] for r in round_stats],
        'Total Seller Surplus': [floor(r['seller surplus'].sum()) for r in round_stats],
        'Total Buyer Surplus': [floor(r['buyer surplus'].sum()) for r in round_stats],
        'Total Surplus': [floor(r['seller surplus'].sum() + r['buyer surplus'].sum()) for r in round_stats],
        'Government Cost': [floor(r['gov cost']) for r in round_stats],
    }
    small_metrics = {
        'Average Quality': [r['avg_quality'] for r in round_stats],
        'Expected Quality': [r['expected_quality'] for r in round_stats],
    }

    fig1 = px.line(pd.DataFrame(big_metrics), title="Market Metrics Over Rounds",
                   labels={"value": "Metric Value", "variable": "Metric"}, markers=True)
    fig1.update_layout(xaxis_title="Round", yaxis_title="Value", height=500)

    fig2 = px.line(pd.DataFrame(small_metrics), title="Average Quality Over Rounds",
                   labels={"value": "Average Quality", "variable": "Round"}, markers=True)
    fig2.update_layout(xaxis_title="Round", yaxis_title="Average Quality", height=500)
    fig2.update_yaxes(range=[0, 1])

    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)
