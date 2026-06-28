import streamlit as st
import pandas as pd
import plotly.express as px
from math import floor

from src.simulation import simulate_market


def _display_round_charts(round_stats):
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
    fig2.update_layout(xaxis_title="Round", yaxis_title="Average Quality", height=500,
                       yaxis=dict(range=[0, 1]))

    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)


def _display_quality_tabs(round_stats, fig0):
    round_tabs = st.tabs(['Round 0'] + [f"Round {r['round']}" for r in round_stats])
    with round_tabs[0]:
        st.markdown("### Initial Seller Quality Distribution (Round 0)")
        st.plotly_chart(fig0, use_container_width=True)
    for tab, r in zip(round_tabs[1:], round_stats):
        with tab:
            st.plotly_chart(r['quality_plot'], use_container_width=True)


def render():
    st.title("Insights and Analysis")
    st.markdown("""
    Without proper policy implementation, asymmetric information leads to market failure over time. Expectation of quality decreases, punishing higher quality sellers and forcing them out of the market leaving less economic activity. As long as the standard deviation from the mean is above 0 (simulating quality variety), the number of sellers will decrease each round. It is for this reason that policies and signaling can be implemented within a market to attempt to keep high quality sellers from leaving.

    Use the quick simulations below to see the effects of various policy tools:
    """)

    st.markdown("---")
    st.markdown("### Basic Simulation")
    st.markdown("This simulation runs with default parameters and no policies applied.")
    if st.button("Run Basic Simulation"):
        with st.spinner("Running basic simulation..."):
            round_stats, fig0, warnings = simulate_market(0.5, 100, 0.3, 5)
        for w in warnings:
            st.warning(w)
        if round_stats is not None:
            st.session_state.basic_results = (round_stats, fig0)

    if 'basic_results' in st.session_state:
        round_stats, fig0 = st.session_state.basic_results
        _display_quality_tabs(round_stats, fig0)
        _display_round_charts(round_stats)
        st.markdown("""
            Without policy implementation or the possibility of signaling, the basic market will fail over time. This conclusion is independant of the initial average quality, standard deviation, or number of sellers. The market will always fail to keep high quality sellers in the market.
            """)

    st.markdown("---")
    st.markdown("### Simulation with Policies")
    st.markdown("This simulation runs with all policies applied, including a minimum quality standard, subsidy for high quality sellers, and penalty for low quality sellers.")
    if st.button("Run Simulation with Subsidy, Penalty, and Minimum Quality"):
        with st.spinner("Running simulation with subsidy and penalty..."):
            round_stats, fig0, warnings = simulate_market(0.5, 100, 0.3, 5, apply_min_quality=True, min_quality=0.3, subsidy_amount=300, penalty_amount=250)
        for w in warnings:
            st.warning(w)
        if round_stats is not None:
            st.session_state.policy_results = (round_stats, fig0)

    if 'policy_results' in st.session_state:
        round_stats, fig0 = st.session_state.policy_results
        _display_quality_tabs(round_stats, fig0)
        _display_round_charts(round_stats)
        st.markdown("""
                    With the implementation of a minimum quality standard, subsidy, and penalty, the market can maintain higher quality sellers over time. The subsidy incentivizes high quality sellers to remain, while the penalty discourages low quality sellers from staying in the market. The minimum quality standard ensures that only sellers above a certain quality threshold are allowed to participate.
                    """)

    st.markdown("---")
    st.markdown("### Simulation with Signaling")
    st.markdown("This simulation runs with signaling enabled, allowing high quality sellers to pay a cost to signal their quality level to buyers.")
    if st.button("Run Simulation with Signaling"):
        with st.spinner("Running simulation with signaling..."):
            round_stats, fig0, warnings = simulate_market(0.5, 100, 0.3, 5, signaling_cost=50, signaling_bonus=500, high_quality_threshold=0.7)
        for w in warnings:
            st.warning(w)
        if round_stats is not None:
            st.session_state.signaling_results = (round_stats, fig0)

    if 'signaling_results' in st.session_state:
        round_stats, fig0 = st.session_state.signaling_results
        _display_quality_tabs(round_stats, fig0)
        _display_round_charts(round_stats)
        st.markdown("""
                    Signaling allows high quality sellers to differentiate themselves from low quality sellers by incurring a cost to signal their quality level. This can lead to a more stable market where high quality sellers are rewarded for their quality, while low quality sellers are discouraged from participating. The signaling bonus must be greater than the signaling cost to incentivize sellers to signal their quality.
                    """)

    st.markdown("---")
    st.markdown("### Overall Conclusions and Connections")
    st.markdown("""
                Examples of Asymmetric Information in the real world include:
                - **Used Car Market**: Sellers may have more information about the quality of the car than buyers, leading to adverse selection.
                - **Job Market**: Employers may not know the true abilities of job candidates, leading to potential mismatches.
                - **Insurance Market**: Insurers may not have complete information about the risk profile of policyholders, leading to moral hazard.

                The government and other institutions can and have intervened in these markets to mitigate the effects of asymmetric information. Examples include:
                - **Used Car Market**: Lemon laws that require sellers to disclose known defects.
                - **Job Market**: Credentialing systems that verify qualifications and skills.
                - **Insurance Market**: Regulations requiring insurers to provide clear information about coverage and risks.

                These interventions can help restore trust in the market, improve efficiency, and ensure that high quality sellers are not driven out of the market due to asymmetric information.
                """)
