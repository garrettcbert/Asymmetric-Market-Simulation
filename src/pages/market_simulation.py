import streamlit as st
import numpy as np
from math import floor

from src.simulation import simulate_market
from src.pages.glossary import expander as glossary_expander


def render():
    st.title("Customizeable Market Simulation")
    st.write("This simulation demonstrates the effects of asymmetric information in a market.")
    glossary_expander()

    st.markdown('<p style="text-align: center"> Policy Parameters: </p>', unsafe_allow_html=True)
    if st.button("Randomize Parameters"):
        st.session_state.apply_min_quality = np.random.choice([True, False])
        st.session_state.min_quality = np.random.uniform(0.0, 1.0) if st.session_state.apply_min_quality else 0.0
        st.session_state.subsidy = np.random.choice([True, False])
        st.session_state.subsidy_amount = np.random.randint(0, 1000) if st.session_state.subsidy else 0
        st.session_state.penalty = np.random.choice([True, False])
        st.session_state.penalty_amount = np.random.randint(0, 1000) if st.session_state.penalty else 0
        st.session_state.signaling = np.random.choice([True, False])
        st.session_state.signaling_cost = np.random.randint(0, 1000) if st.session_state.signaling else 0
        st.session_state.signaling_bonus = np.random.randint(0, 1000) if st.session_state.signaling else 0
        st.session_state.high_quality_threshold = np.random.uniform(0.5, 1.0)
        st.session_state.low_quality_threshold = np.random.uniform(0.0, 0.5)
        st.session_state.avg_quality = np.random.uniform(0.0, 1.0)
        st.session_state.std_quality = np.random.uniform(0.0, 0.5)
        st.session_state.num_sellers = np.random.randint(1, 500)
        st.session_state.num_rounds = np.random.randint(1, 10)
    else:
        defaults = {
            'apply_min_quality': False, 'min_quality': 0.3,
            'subsidy': False, 'subsidy_amount': 400,
            'penalty': False, 'penalty_amount': 400,
            'signaling': False, 'signaling_cost': 50, 'signaling_bonus': 400,
            'high_quality_threshold': 0.7, 'low_quality_threshold': 0.3,
            'avg_quality': 0.5, 'std_quality': 0.3,
            'num_sellers': 200, 'num_rounds': 5,
        }
        for key, val in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = val

    apply_min_quality = st.checkbox("Apply Minimum Quality Standard", value=st.session_state.get('apply_min_quality', False))
    if apply_min_quality:
        min_quality = st.slider("Minimum Quality Standard", 0.0, 1.0, st.session_state.get('min_quality', 0.5), 0.01)
        st.warning("Minimum Quality Standard is applied. Sellers with quality below the standard will be removed.")

    subsidy = st.checkbox("Apply Subsidy", value=st.session_state.get('subsidy', False))
    if subsidy:
        subsidy_amount = st.number_input("Subsidy Amount (per seller)", min_value=0, max_value=1000, value=st.session_state.get('subsidy_amount', 100), step=10)
        st.warning(f"Subsidy of {subsidy_amount} will be applied to sellers with quality above high quality threshold (default 0.7).")

    penalty = st.checkbox("Apply Penalty", value=st.session_state.get('penalty', False))
    if penalty:
        penalty_amount = st.number_input("Penalty Amount (per seller)", min_value=0, max_value=1000, value=st.session_state.get('penalty_amount', 100), step=10)
        st.warning(f"Penalty of {penalty_amount} will be applied to sellers with quality below low quality threshold (default 0.3).")

    signaling = st.checkbox("Enable Signaling", value=st.session_state.get('signaling', False))
    if signaling:
        signaling_cost = st.number_input("Signaling Cost", min_value=0, max_value=1000, value=st.session_state.get('signaling_cost', 50), step=10)
        signaling_bonus = st.number_input("Signaling Bonus", min_value=0, max_value=1000, value=st.session_state.get('signaling_bonus', 100), step=10)
        if signaling_bonus <= signaling_cost:
            st.error("Signaling bonus must be greater than signaling cost to incentivize signaling.")
        else:
            st.warning(f"Signaling enabled: Sellers with quality above the high quality threshold will incur a cost of {signaling_cost} but receive a bonus of {signaling_bonus}.")

    high_quality_threshold = st.slider("High Quality Threshold", 0.0, 1.0, st.session_state.get('high_quality_threshold', 0.7), 0.01)
    low_quality_threshold = st.slider("Low Quality Threshold", 0.0, 1.0, st.session_state.get('low_quality_threshold', 0.3), 0.01)

    st.markdown('<p style="text-align: center"> Simulation Parameters: </p>', unsafe_allow_html=True)
    avg_quality = st.slider("Starting average quality", 0.0, 1.0, st.session_state.get('avg_quality', 0.5), 0.01)
    std_quality = st.slider("Quality Standard Deviation", 0.0, 0.5, st.session_state.get('std_quality', 0.1), 0.01)
    num_sellers = st.number_input("Number of sellers", min_value=1, max_value=500, value=st.session_state.get('num_sellers', 100))
    num_rounds = st.slider("Number of rounds", 1, 10, st.session_state.get('num_rounds', 5))

    tab1, tab2 = st.tabs(["Simulation", "Data Table"])
    round_stats = []

    with tab1:
        if st.button("Run Simulation"):
            sim_kwargs = {}
            if apply_min_quality:
                sim_kwargs["apply_min_quality"] = True
                sim_kwargs["min_quality"] = min_quality
            if subsidy:
                sim_kwargs["subsidy_amount"] = subsidy_amount
            if penalty:
                sim_kwargs["penalty_amount"] = penalty_amount
            if signaling:
                sim_kwargs["signaling_cost"] = signaling_cost
                sim_kwargs["signaling_bonus"] = signaling_bonus

            with st.spinner("Simulating market..."):
                round_stats, fig0, sim_warnings = simulate_market(
                    avg_quality, num_sellers, std_quality, num_rounds,
                    high_quality_threshold=high_quality_threshold,
                    low_quality_threshold=low_quality_threshold,
                    **sim_kwargs
                )

            for w in sim_warnings:
                st.warning(w)

            if round_stats is None:
                return

            st.session_state.round_stats = round_stats
            round_tabs = st.tabs(["Round 0"] + [f"Round {r['round']}" for r in round_stats])
            with round_tabs[0]:
                st.markdown("### Initial Seller Quality Distribution (Round 0)")
                st.plotly_chart(fig0, use_container_width=True)
            for tab, r in zip(round_tabs[1:], round_stats):
                with tab:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Market Price", f"${r['market_price']}")
                        st.metric("Sellers Remaining", r['num_sales'])
                    with col2:
                        st.metric("Average Quality", f"{r['avg_quality']:.2f}")
                        st.metric("Total Seller Surplus", f"${floor(r['seller surplus'].sum())}")
                    with col3:
                        st.metric("Total Buyer Surplus", f"${floor(r['buyer surplus'].sum())}")
                        st.metric("Total Surplus", f"${floor(r['seller surplus'].sum() + r['buyer surplus'].sum())}")
                    st.divider()
                    with st.expander("Quality Distribution", expanded=True):
                        st.plotly_chart(r['quality_plot'], use_container_width=True)
                    with st.expander("Surplus Distribution", expanded=True):
                        st.plotly_chart(r['surplus_plot'], use_container_width=True)
        else:
            st.write("Adjust the parameters and click 'Run Simulation' to see the results.")

    with tab2:
        st.header("Seller Data")
        if round_stats:
            round_tabs = st.tabs([f"Round {r['round']}" for r in round_stats])
            for tab, r in zip(round_tabs, round_stats):
                with tab:
                    st.subheader(f"Round {r['round']}")
                    st.dataframe(r['dataframe'])
        else:
            st.write("No simulation data to display yet.")
