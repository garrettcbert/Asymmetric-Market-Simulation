import streamlit as st
import plotly.graph_objects as go
import plotly.subplots as sp
from math import floor

from src.simulation import simulate_market
from src.pages.glossary import expander as glossary_expander


def render():
    st.title("Policy Comparisons")
    st.markdown("Compare the effects of different policies on market outcomes.")
    glossary_expander()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Market 1 Settings")
        st.write("Adjust the parameters for Market 1.")
        apply_min_quality1 = st.checkbox("Apply Minimum Quality Standard (Market 1)", value=False)
        if apply_min_quality1:
            min_quality1 = st.slider("Minimum Quality Standard (Market 1)", 0.0, 1.0, 0.5, 0.01)
            st.warning("Minimum Quality Standard is applied. Sellers with quality below the standard will be removed.")
        else:
            min_quality1 = 0
        subsidy1 = st.checkbox("Apply Subsidy (Market 1)", value=False)
        if subsidy1:
            subsidy_amount1 = st.number_input("Subsidy Amount (Market 1)", min_value=0, max_value=1000, value=100, step=10)
            st.warning(f"Subsidy of {subsidy_amount1} will be applied to sellers with quality above high quality threshold (default 0.7).")
        else:
            subsidy_amount1 = 0
        penalty1 = st.checkbox("Apply Penalty (Market 1)", value=False)
        if penalty1:
            penalty_amount1 = st.number_input("Penalty Amount (Market 1)", min_value=0, max_value=1000, value=100, step=10)
            st.warning(f"Penalty of {penalty_amount1} will be applied to sellers with quality below low quality threshold (default 0.3).")
        else:
            penalty_amount1 = 0
        signaling1 = st.checkbox("Enable Signaling (Market 1)", value=False)
        if signaling1:
            signaling_cost1 = st.number_input("Signaling Cost (Market 1)", min_value=0, max_value=1000, value=50, step=10)
            signaling_bonus1 = st.number_input("Signaling Bonus (Market 1)", min_value=0, max_value=1000, value=100, step=10)
            if signaling_bonus1 <= signaling_cost1:
                st.error("Signaling bonus must be greater than signaling cost to incentivize signaling.")
            else:
                st.warning(f"Signaling enabled: Sellers with quality above the high quality threshold will incur a cost of {signaling_cost1} but receive a bonus of {signaling_bonus1}.")
        else:
            signaling_cost1 = 0
            signaling_bonus1 = 0
        high_quality_threshold1 = st.slider("High Quality Threshold (Market 1)", 0.0, 1.0, 0.7, 0.01)
        low_quality_threshold1 = st.slider("Low Quality Threshold (Market 1)", 0.0, 1.0, 0.3, 0.01)
        market1_avg_quality = st.slider("Starting average quality (Market 1)", 0.0, 1.0, 0.5, 0.01)
        market1_num_sellers = st.number_input("Number of sellers (Market 1)", min_value=1, max_value=500, value=100)
        market1_num_rounds = st.slider("Number of rounds (Market 1)", 1, 10, 5)

    with col2:
        st.subheader("Market 2 Settings")
        st.write("Adjust the parameters for Market 2.")
        apply_min_quality2 = st.checkbox("Apply Minimum Quality Standard (Market 2)", value=False)
        if apply_min_quality2:
            min_quality2 = st.slider("Minimum Quality Standard (Market 2)", 0.0, 1.0, 0.5, 0.01)
            st.warning("Minimum Quality Standard is applied. Sellers with quality below the standard will be removed.")
        else:
            min_quality2 = 0
        subsidy2 = st.checkbox("Apply Subsidy (Market 2)", value=False)
        if subsidy2:
            subsidy_amount2 = st.number_input("Subsidy Amount (Market 2)", min_value=0, max_value=1000, value=100, step=10)
            st.warning(f"Subsidy of {subsidy_amount2} will be applied to sellers with quality above high quality threshold (default 0.7).")
        else:
            subsidy_amount2 = 0
        penalty2 = st.checkbox("Apply Penalty (Market 2)", value=False)
        if penalty2:
            penalty_amount2 = st.number_input("Penalty Amount (Market 2)", min_value=0, max_value=1000, value=100, step=10)
            st.warning(f"Penalty of {penalty_amount2} will be applied to sellers with quality below low quality threshold (default 0.3).")
        else:
            penalty_amount2 = 0
        signaling2 = st.checkbox("Enable Signaling (Market 2)", value=False)
        if signaling2:
            signaling_cost2 = st.number_input("Signaling Cost (Market 2)", min_value=0, max_value=1000, value=50, step=10)
            signaling_bonus2 = st.number_input("Signaling Bonus (Market 2)", min_value=0, max_value=1000, value=100, step=10)
            if signaling_bonus2 <= signaling_cost2:
                st.error("Signaling bonus must be greater than signaling cost to incentivize signaling.")
            else:
                st.warning(f"Signaling enabled: Sellers with quality above the high quality threshold will incur a cost of {signaling_cost2} but receive a bonus of {signaling_bonus2}.")
        else:
            signaling_cost2 = 0
            signaling_bonus2 = 0
        high_quality_threshold2 = st.slider("High Quality Threshold (Market 2)", 0.0, 1.0, 0.7, 0.01)
        low_quality_threshold2 = st.slider("Low Quality Threshold (Market 2)", 0.0, 1.0, 0.3, 0.01)
        market2_avg_quality = st.slider("Starting average quality (Market 2)", 0.0, 1.0, 0.5, 0.01)
        market2_num_sellers = st.number_input("Number of sellers (Market 2)", min_value=1, max_value=500, value=100)
        market2_num_rounds = st.slider("Number of rounds (Market 2)", 1, 10, 5)

    if st.button("Run both markets"):
        with st.spinner("Running simulations..."):
            m1_stats, _, m1_warnings = simulate_market(
                market1_avg_quality, market1_num_sellers, 0.1, market1_num_rounds,
                apply_min_quality=apply_min_quality1, min_quality=min_quality1,
                subsidy_amount=subsidy_amount1, penalty_amount=penalty_amount1,
                signaling_cost=signaling_cost1, signaling_bonus=signaling_bonus1,
                high_quality_threshold=high_quality_threshold1, low_quality_threshold=low_quality_threshold1
            )
            m2_stats, _, m2_warnings = simulate_market(
                market2_avg_quality, market2_num_sellers, 0.1, market2_num_rounds,
                apply_min_quality=apply_min_quality2, min_quality=min_quality2,
                subsidy_amount=subsidy_amount2, penalty_amount=penalty_amount2,
                signaling_cost=signaling_cost2, signaling_bonus=signaling_bonus2,
                high_quality_threshold=high_quality_threshold2, low_quality_threshold=low_quality_threshold2
            )

        for w in m1_warnings + m2_warnings:
            st.warning(w)

        if m1_stats and m2_stats:
            round_tabs = st.tabs([f"Round {i+1}" for i in range(len(m1_stats))])
            for tab, (r1, r2) in zip(round_tabs, zip(m1_stats, m2_stats)):
                with tab:
                    st.markdown(f"### Round {r1['round']} Comparison")
                    with st.container():
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Quality Difference", f"{(r1['avg_quality'] - r2['avg_quality']):.2f}", delta_color="inverse")
                        with col2:
                            st.metric("Price Difference", f"{(r1['market_price'] - r2['market_price'])}")
                        with col3:
                            st.metric("Sellers Difference", f"{(r1['num_sellers'] - r2['num_sellers'])}")

                    st.markdown("#### Quality Distribution Comparison")
                    quality_fig = sp.make_subplots(rows=1, cols=2, shared_yaxes=True,
                                                   subplot_titles=("Market 1 Quality", "Market 2 Quality"))
                    quality_fig.add_trace(go.Histogram(x=r1['dataframe']['Individual Quality'], name='Market 1', marker_color='#1f77b4', opacity=0.7), row=1, col=1)
                    quality_fig.add_trace(go.Histogram(x=r2['dataframe']['Individual Quality'], name='Market 2', marker_color='#ff7f0e', opacity=0.7), row=1, col=2)
                    quality_fig.add_vline(x=r1['avg_quality'], line_dash="dash", line_color="red", annotation_text=f"Avg: {r1['avg_quality']:.2f}", annotation_position="top right", row=1, col=1)
                    quality_fig.add_vline(x=r2['avg_quality'], line_dash="dash", line_color="red", annotation_text=f"Avg: {r2['avg_quality']:.2f}", annotation_position="top right", row=1, col=2)
                    quality_fig.update_layout(height=400, showlegend=False, bargap=0.1, xaxis_title="Quality", xaxis2_title="Quality", yaxis_title="Count")
                    max_quality = max(max(r1['dataframe']['Individual Quality']), max(r2['dataframe']['Individual Quality'])) * 1.1
                    max_count = max(len(r1['dataframe']), len(r2['dataframe'])) * 1.1
                    quality_fig.update_xaxes(range=[0, max_quality])
                    quality_fig.update_yaxes(range=[0, max_count])
                    st.plotly_chart(quality_fig, use_container_width=True)

                    st.markdown("#### Seller Surplus Comparison")
                    surplus_fig = sp.make_subplots(rows=1, cols=2, shared_yaxes=True,
                                                   subplot_titles=("Market 1 Seller Surplus", "Market 2 Seller Surplus"))
                    surplus_fig.add_trace(go.Histogram(x=r1['dataframe']['Seller Surplus'], name='Market 1', marker_color='#1f77b4', opacity=0.7), row=1, col=1)
                    surplus_fig.add_trace(go.Histogram(x=r2['dataframe']['Seller Surplus'], name='Market 2', marker_color='#ff7f0e', opacity=0.7), row=1, col=2)
                    surplus_fig.add_vline(x=r1['dataframe']['Seller Surplus'].mean(), line_dash="dash", line_color="orange", annotation_text=f"Avg: {r1['dataframe']['Seller Surplus'].mean():.2f}", annotation_position="top right", row=1, col=1)
                    surplus_fig.add_vline(x=r2['dataframe']['Seller Surplus'].mean(), line_dash="dash", line_color="orange", annotation_text=f"Avg: {r2['dataframe']['Seller Surplus'].mean():.2f}", annotation_position="top right", row=1, col=2)
                    surplus_fig.update_layout(height=400, showlegend=False, bargap=0.1, xaxis_title="Seller Surplus", xaxis2_title="Seller Surplus", yaxis_title="Count")
                    max_surplus = max(max(r1['dataframe']['Seller Surplus']), max(r2['dataframe']['Seller Surplus'])) * 1.1
                    surplus_fig.update_xaxes(range=[0, max_surplus])
                    surplus_fig.update_yaxes(range=[0, max_count])
                    st.plotly_chart(surplus_fig, use_container_width=True)

                    with st.expander("Market 1 Data"):
                        st.dataframe(r1['dataframe'])
                    with st.expander("Market 2 Data"):
                        st.dataframe(r2['dataframe'])

            st.markdown("### Final Round Comparison")
            final_r1 = m1_stats[-1]
            final_r2 = m2_stats[-1]
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Market 1 Final Results**")
                st.metric("Average Quality", f"{final_r1['avg_quality']:.2f}")
                st.metric("Market Price", final_r1['market_price'])
                st.metric("Sellers Remaining", final_r1['num_sales'])
                st.metric("Total Surplus", floor(final_r1['seller surplus'].sum() + final_r1['buyer surplus'].sum()))
            with col2:
                st.markdown("**Market 2 Final Results**")
                st.metric("Average Quality", f"{final_r2['avg_quality']:.2f}")
                st.metric("Market Price", final_r2['market_price'])
                st.metric("Sellers Remaining", final_r2['num_sales'])
                st.metric("Total Surplus", floor(final_r2['seller surplus'].sum() + final_r2['buyer surplus'].sum()))
        else:
            st.error("One or both markets did not run successfully.")
