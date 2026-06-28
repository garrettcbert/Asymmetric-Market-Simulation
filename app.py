import streamlit as st
import numpy as np
from math import floor
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.subplots as sp


def simulate_market(avg_quality, num_sellers, std_quality, num_rounds, apply_min_quality=False, min_quality=0,
                    subsidy_amount=0, penalty_amount=0, signaling_cost=0, signaling_bonus=0, high_quality_threshold=0.7, low_quality_threshold=0.3):
        
    initial_quality = np.clip(np.random.normal(avg_quality, std_quality, num_sellers), 0, 1)
    if apply_min_quality:
        initial_quality[initial_quality < min_quality] = np.nan
        initial_quality = initial_quality[~np.isnan(initial_quality)]
        num_sellers = len(initial_quality)
        if num_sellers == 0:
            st.warning("No sellers meet the minimum quality standard. Simulation ends early.")
            return None, None
    
    fig0 = go.Figure()
    fig0.add_trace(go.Histogram(
        x=initial_quality,
        nbinsx=40,
        marker_color='gray',
        marker_line_color='black',
        marker_line_width=1
    ))
    fig0.add_vline(
        x=np.mean(initial_quality),
        line_dash="dash",
        line_color="purple",
        annotation_text="Initial Avg Quality",
        annotation_position="top right"
    )
    fig0.update_layout(
        title="Round 0: Initial Sellers' Quality",
        xaxis_title="Quality",
        yaxis_title="Count",
        xaxis=dict(range=[0, 1], dtick=0.1),
        bargap=0.1
    )

    round_stats = []
    gov_cost = 0

    for round_num in range(1, num_rounds + 1):
        if round_num == 1:
            old_quality = initial_quality.copy()
        else:
            old_quality = quality.copy()

        signals_sent = np.zeros(len(old_quality), dtype=bool)

        if signaling_cost > 0 and signaling_bonus > signaling_cost:
            signals_sent = old_quality > high_quality_threshold

            
        expected_quality = np.mean(old_quality)
        seller_values = old_quality * 1000
        market_price = floor(expected_quality * 1000)

        exp_payout = np.full(len(old_quality), market_price, dtype = float) + np.where(signals_sent, signaling_bonus, 0) - np.where(signals_sent, signaling_cost, 0)

        for seller in range(len(old_quality)):
            if subsidy_amount > 0 and old_quality[seller] > high_quality_threshold:
                gov_cost += subsidy_amount
                exp_payout[seller] += subsidy_amount
            elif penalty_amount > 0 and old_quality[seller] < low_quality_threshold:
                gov_cost -= penalty_amount
                exp_payout[seller] -= penalty_amount
            
        sales = exp_payout >= seller_values
        quality = old_quality[sales]

        if len(quality) == 0:
            st.warning(f"Simulation ended early at Round {round_num}: no sellers remain. Rounds stop because there are no more sellers able to participate in the market.")
            break
        
        sellers = pd.DataFrame({
            'Individual Quality': old_quality,
            'Expected Quality': expected_quality,
            'Market Price': market_price,
            'Seller Valuation': seller_values,
            'Expected Payout' : exp_payout,
            'Sells' : sales,
            'Seller Surplus': np.where(sales, exp_payout - seller_values, 0),
            'Buyer Surplus': np.where(sales, seller_values - market_price, 0),
            'Total Social Surplus': np.where(sales, exp_payout - seller_values, 0) + np.where(sales, seller_values - market_price, 0) - gov_cost,
            'Penalty Amount': penalty_amount,
            'Subsidy Amount': subsidy_amount,
            'Government Cost' : gov_cost,
            'High Quality': np.where(old_quality > high_quality_threshold, True, False),
            'Low Quality': np.where(old_quality < low_quality_threshold, True, False),
            'Net Signaling': np.where(signals_sent, signaling_bonus - signaling_cost, 0)
        })

        remaining_sellers = sellers[sellers['Sells']]
        num_sales = len(remaining_sellers)


        if num_sales == 0:
            st.warning("No sellers were able to sell. Simulation ends early.")
            break
        if avg_quality == 0:
            st.warning("Average quality is 0. Simulation ends early.")
            break
        
        avg_quality = remaining_sellers['Individual Quality'].mean()


        fig = go.Figure()

        fig.add_trace(go.Histogram(
            x=remaining_sellers['Individual Quality'],
            nbinsx=40,
            marker_color='skyblue',
            marker_line_color='black',
            marker_line_width=1,
            name='Quality Distribution',
            xbins=dict(start=0, end=1, size=0.025)
        ))


        fig.add_vline(
            x=avg_quality,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Avg Quality: {avg_quality:.2f}",
            annotation_position="top left"
        )

        fig.add_vline(
            x=expected_quality,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Expected Quality: {expected_quality:.2f}",
            annotation_position="top right"
        )

        fig.update_layout(
            title=f"Round {round_num}: Remaining Sellers' Quality",
            xaxis_title="Quality",
            yaxis_title="Count",
            xaxis=dict(range=[0, 1], dtick=0.1),
            bargap=0.1,
            height=500
        )
        surplus_fig = go.Figure()

        max_abs_value = max(sellers['Buyer Surplus'].max(), sellers['Seller Surplus'].max())
        x_range = [-max_abs_value * 1.1, max_abs_value * 1.1]


        surplus_fig.add_trace(go.Histogram(
            x=sellers['Seller Surplus'],
            nbinsx=40,
            marker_color='lightgreen',
            marker_line_color='black',
            marker_line_width=1,
            name='Seller Surplus',
            opacity=0.7
        ))


        buyer_surplus_negative = sellers['Buyer Surplus']
        surplus_fig.add_trace(go.Histogram(
            x=buyer_surplus_negative,
            nbinsx=40,
            marker_color='lightcoral',
            marker_line_color='black',
            marker_line_width=1,
            name='Buyer Surplus',
            opacity=0.7
        ))


        surplus_fig.add_vline(
            x=sellers['Buyer Surplus'].mean(),
            line_dash="dash",
            line_color="yellow",
            annotation_text=f"Avg Buyer Surplus: {sellers['Buyer Surplus'].mean():.2f}",
            annotation_position="top left"
        )

        surplus_fig.add_vline(
            x=sellers['Seller Surplus'].mean(),
            line_dash="dash",
            line_color="orange",
            annotation_text=f"Avg Seller Surplus: {sellers['Seller Surplus'].mean():.2f}",
            annotation_position="top right"
        )


        surplus_fig.add_vline(
            x = sellers['Buyer Surplus'].sum() + sellers['Seller Surplus'].sum() - sellers['Government Cost'].sum(),
            line_dash="dash",
            line_color="white",
            annotation_text="Total Social Surplus",
            annotation_position="top"
        )    


        surplus_fig.update_layout(
            title=f"Round {round_num}: Surplus Distribution (Buyer vs Seller)",
            xaxis_title="Surplus (Negative = Buyer, Positive = Seller)",
            yaxis_title="Count",
            xaxis=dict(
                range=x_range,
                tickvals=[i for i in range(-1000, 1100, 200)],
                ticktext=[str(abs(i)) for i in range(-1000, 1100, 200)]
            ),
            bargap=0.1,
            height=500,
            barmode='overlay',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        num_sellers = num_sales
        round_stats.append({
        'round': round_num,
        'market_price': market_price,
        'avg_quality': avg_quality,
        'expected_quality': expected_quality,
        'num_sellers': num_sellers,
        'num_sales': num_sales,
        'quality_plot': fig,
        'surplus_plot': surplus_fig,
        'seller surplus': sellers['Seller Surplus'],
        'buyer surplus': sellers['Buyer Surplus'],
        'gov cost': gov_cost,
        'dataframe' : sellers
    })
        
    return round_stats, fig0

st.set_page_config(page_title="Asymmetric Information Market Simulation", layout="wide")
st.sidebar.title("Asymmetric Information Market Simulation")
st.sidebar.markdown("Select a section to explore the simulation and its insights.")
selection = st.sidebar.radio("Go to", ["About", "Market Simulation", "Policy Comparisons", "Full Data View", "Insights and Analysis", "Glossary"])


if selection == "About":
    st.title("About the Simulation")
    st.markdown("""
## Introduction
This model is inspired by the work of George Akerlof, Nobel laureate in Economics and creator of the ‘Akerlof’s Lemons’ model Akerlof’s model seeks to illustrate how Asymmetric Information can lead to market failure over time in markets with quality level variety.
""")
    st.image("https://www.nobelprize.org/images/akerlof-13727-content-portrait-mobile-tiny.jpg", caption="George Akerlof, Nobel Laureate in Economics", width = 200)
    st.markdown("""
## What is Asymmetric Information?
In a market seeking to maximize total surplus, both buyers and sellers have perfect information about the quality of the product on the market. For example, the grocery store sells many products at a price that matches the supply and demand market in which everyone is aware about the quality. I know the quality of the cereal when I purchase it and so does the seller, which is why the prices for different types of cereal can vary so much. In the instance of asymmetric information, only the seller knows the true quality of the product being sold. The following simulation highlights the loss of economic activity due to the lack of perfect information as well as some policies that shift the effects of asymmetric information.

## How the Simulation Works
Using a randomized distribution forming a normal approximation (bell curve) around a given quality mark, we can simulate rounds where:  
- Buyers pay in their best interest  
- Sellers act in their best interest (staying or leaving the market)  
- Policies are introduced to see how they can impact the market  

The results of each round are shown in the next round and the metrics are shown along with it. Policy parameters and the option of signaling explained below can be implemented. Additionally, the average quality, the number of sellers, the standard deviation of the quality marks, and the number of rounds being simulated can all be customized to simulate different distinct market situations.
    """)


elif selection == "Market Simulation":
    st.title("Customizeable Market Simulation")
    st.write("This simulation demonstrates the effects of asymmetric information in a market.")
    st.expander("Glossary", expanded=False).markdown("""
### Simulation Parameters
- **Starting Average Quality**: The average quality of the initial randomization of the quality of sellers (normal randomization will result in bell curve centered on this value)  
- **Quality Standard Deviation**: The standard deviation of the initial randomization of the quality of sellers from the average quality  
- **Number of Sellers**: The number of sellers along with their quality being randomized 
- **Number of Rounds**: The number of rounds to simulate in the market (each round will show the results of the previous round)

--- 

### Policy Parameters
- **Minimum Quality Standard**: The lowest acceptable quality allowed to enter the market (removes all sellers holding qualities below this value)  
- **Subsidy**: A government extra payment to sellers with a quality above the high quality threshold  
- **Penalty**: A government tax to the sellers with a quality below the low quality threshold  
- **Signaling**: Enables sellers with a quality above the high quality threshold to pay a cost to signal their high quality level to buyers who in turn pay a bonus to these sellers  
- **Signaling Cost**: Cost of acquiring the signal (think price of a college degree)  
- **Signaling Bonus**: Bonus allotted to sellers as a result of the signal (must be higher than cost to incentivize)  
- **High Quality Threshold**: Value marking any quality equal to or below as ‘high quality’  
- **Low Quality Threshold**: Value marking any quality equal to or below as ‘low quality’ 
                                                     
---
                                                     
### Insight Metrics
- **Expected Quality**: Average quality of sellers currently in the market  
- **Market Price**: Example scaled price that buyers are set to pay for a quality (in this simulation: mp = expected quality * 1000)  
- **Seller’s Valuation**: A sellers’ own valuation of their product (individual quality * 1000 without policies or signaling)  
- **Expected Payout**: The payout that the seller perceives as receiving in staying in the market (will leave if seller valuation is less than expected payout)  
- **Sells**: Whether or not the seller would stay in the market (True if seller valuation is less than or equal to expected payout)  
- **Seller Surplus**: The difference between the sellers’ valuation and the expected payout if the payout is greater than or equal to the valuation  
- **Buyer Surplus**: The difference between the sellers’ valuation and the market price  
- **Government Cost**: The cost the government incurs from penalties or subsidies  
- **Total Social Surplus**: The sum of the buyer and seller surplus minus the government cost with penalties or subsidies  
- **Penalty Amount**: The tax on the payout to sellers below the low quality threshold  
- **Subsidy Amount**: The addition to the payout to sellers above the high quality threshold  
- **High Quality**: True if individual quality is greater than or equal to high quality threshold  
- **Low Quality**: True if individual quality is less than or equal to low quality threshold  
- **Net Signaling**: Addition to the payout as a result of signaling (signaling bonus - signaling cost)
    """)
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
        if 'apply_min_quality' not in st.session_state:
            st.session_state.apply_min_quality = False
        if 'min_quality' not in st.session_state:
            st.session_state.min_quality = 0.3
        if 'subsidy' not in st.session_state:
            st.session_state.subsidy = False
        if 'subsidy_amount' not in st.session_state:
            st.session_state.subsidy_amount = 400
        if 'penalty' not in st.session_state:
            st.session_state.penalty = False
        if 'penalty_amount' not in st.session_state:
            st.session_state.penalty_amount = 400
        if 'signaling' not in st.session_state:
            st.session_state.signaling = False
        if 'signaling_cost' not in st.session_state:
            st.session_state.signaling_cost = 50
        if 'signaling_bonus' not in st.session_state:
            st.session_state.signaling_bonus = 400
        if 'high_quality_threshold' not in st.session_state:
            st.session_state.high_quality_threshold = 0.7
        if 'low_quality_threshold' not in st.session_state:
            st.session_state.low_quality_threshold = 0.3
        if 'avg_quality' not in st.session_state:
            st.session_state.avg_quality = 0.5
        if 'std_quality' not in st.session_state:
            st.session_state.std_quality = 0.3
        if 'num_sellers' not in st.session_state:
            st.session_state.num_sellers = 200
        if 'num_rounds' not in st.session_state:
            st.session_state.num_rounds = 5

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
                results = simulate_market(
                avg_quality, num_sellers, std_quality, num_rounds, high_quality_threshold = high_quality_threshold, low_quality_threshold=low_quality_threshold, **sim_kwargs
            )
            st.session_state.round_stats = results[0]
            round_stats = st.session_state.round_stats
            fig0 = results[1]
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
                        st.metric("Average Quality", 
                                f"{r['avg_quality']:.2f}"
                                )
                        st.metric("Total Seller Surplus", 
                                f"${floor(r['seller surplus'].sum())}"
                                )
                    
                    with col3:
                        st.metric("Total Buyer Surplus", 
                                f"${floor(r['buyer surplus'].sum())}"
                                )
                        st.metric("Total Surplus", 
                                f"${floor(r['seller surplus'].sum() + r['buyer surplus'].sum())}"
                                )
                    

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

elif selection == "Policy Comparisons":
    st.title("Policy Comparisons")
    st.markdown("""
    Compare the effects of different policies on market outcomes.
    """)
    st.expander("Glossary", expanded=False).markdown("""
### Simulation Parameters
- **Starting Average Quality**: The average quality of the initial randomization of the quality of sellers (normal randomization will result in bell curve centered on this value)  
- **Quality Standard Deviation**: The standard deviation of the initial randomization of the quality of sellers from the average quality  
- **Number of Sellers**: The number of sellers along with their quality being randomized 
- **Number of Rounds**: The number of rounds to simulate in the market (each round will show the results of the previous round)

--- 

### Policy Parameters
- **Minimum Quality Standard**: The lowest acceptable quality allowed to enter the market (removes all sellers holding qualities below this value)  
- **Subsidy**: A government extra payment to sellers with a quality above the high quality threshold  
- **Penalty**: A government tax to the sellers with a quality below the low quality threshold  
- **Signaling**: Enables sellers with a quality above the high quality threshold to pay a cost to signal their high quality level to buyers who in turn pay a bonus to these sellers  
- **Signaling Cost**: Cost of acquiring the signal (think price of a college degree)  
- **Signaling Bonus**: Bonus allotted to sellers as a result of the signal (must be higher than cost to incentivize)  
- **High Quality Threshold**: Value marking any quality equal to or below as ‘high quality’  
- **Low Quality Threshold**: Value marking any quality equal to or below as ‘low quality’ 
                                                     
---
                                                     
### Insight Metrics
- **Expected Quality**: Average quality of sellers currently in the market  
- **Market Price**: Example scaled price that buyers are set to pay for a quality (in this simulation: mp = expected quality * 1000)  
- **Seller’s Valuation**: A sellers’ own valuation of their product (individual quality * 1000 without policies or signaling)  
- **Expected Payout**: The payout that the seller perceives as receiving in staying in the market (will leave if seller valuation is less than expected payout)  
- **Sells**: Whether or not the seller would stay in the market (True if seller valuation is less than or equal to expected payout)  
- **Seller Surplus**: The difference between the sellers’ valuation and the expected payout if the payout is greater than or equal to the valuation  
- **Buyer Surplus**: The difference between the sellers’ valuation and the market price  
- **Government Cost**: The cost the government incurs from penalties or subsidies  
- **Total Social Surplus**: The sum of the buyer and seller surplus minus the government cost with penalties or subsidies  
- **Penalty Amount**: The tax on the payout to sellers below the low quality threshold  
- **Subsidy Amount**: The addition to the payout to sellers above the high quality threshold  
- **High Quality**: True if individual quality is greater than or equal to high quality threshold  
- **Low Quality**: True if individual quality is less than or equal to low quality threshold  
- **Net Signaling**: Addition to the payout as a result of signaling (signaling bonus - signaling cost)
    """)
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

    st.title("Policy Comparisons")
    st.markdown("""
    Compare the effects of different policies on market outcomes.
    """)
    

    
    if st.button("Run both markets"):
        with st.spinner("Running simulations..."):
            market1_results = simulate_market(market1_avg_quality, market1_num_sellers, 0.1, market1_num_rounds,
                                            apply_min_quality=apply_min_quality1, min_quality=min_quality1,
                                            subsidy_amount=subsidy_amount1, penalty_amount=penalty_amount1,
                                            signaling_cost=signaling_cost1, signaling_bonus=signaling_bonus1,
                                            high_quality_threshold=high_quality_threshold1, low_quality_threshold=low_quality_threshold1)
            
            market2_results = simulate_market(market2_avg_quality, market2_num_sellers, 0.1, market2_num_rounds,
                                            apply_min_quality=apply_min_quality2, min_quality=min_quality2,
                                            subsidy_amount=subsidy_amount2, penalty_amount=penalty_amount2,
                                            signaling_cost=signaling_cost2, signaling_bonus=signaling_bonus2,
                                            high_quality_threshold=high_quality_threshold2, low_quality_threshold=low_quality_threshold2)

        if market1_results and market2_results:
            round_tabs = st.tabs([f"Round {i+1}" for i in range(len(market1_results[0]))])
            
            for tab, (r1, r2) in zip(round_tabs, zip(market1_results[0], market2_results[0])):
                with tab:
                    st.markdown(f"### Round {r1['round']} Comparison")
                    

                    with st.container():
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Quality Difference", 
                                     f"{(r1['avg_quality'] - r2['avg_quality']):.2f}",
                                     delta_color="inverse")
                        with col2:
                            st.metric("Price Difference", 
                                     f"{(r1['market_price'] - r2['market_price'])}")
                        with col3:
                            st.metric("Sellers Difference", 
                                     f"{(r1['num_sellers'] - r2['num_sellers'])}")
                    
                    st.markdown("#### Quality Distribution Comparison")
                    quality_fig = sp.make_subplots(rows=1, cols=2, 
                                              shared_yaxes=True,
                                              subplot_titles=("Market 1 Quality", "Market 2 Quality"))
                    

                    quality_fig.add_trace(
                        go.Histogram(
                            x=r1['dataframe']['Individual Quality'],
                            name='Market 1',
                            marker_color='#1f77b4',
                            opacity=0.7
                        ),
                        row=1, col=1
                    )
                    

                    quality_fig.add_trace(
                        go.Histogram(
                            x=r2['dataframe']['Individual Quality'],
                            name='Market 2',
                            marker_color='#ff7f0e',
                            opacity=0.7
                        ),
                        row=1, col=2
                    )
                    

                    quality_fig.add_vline(
                        x=r1['avg_quality'],
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"Avg: {r1['avg_quality']:.2f}",
                        annotation_position="top right",
                        row=1, col=1
                    )
                    
                    quality_fig.add_vline(
                        x=r2['avg_quality'],
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"Avg: {r2['avg_quality']:.2f}",
                        annotation_position="top right",
                        row=1, col=2
                    )

                    quality_fig.update_layout(
                        height=400,
                        showlegend=False,
                        bargap=0.1,
                        xaxis_title="Quality",
                        xaxis2_title="Quality",
                        yaxis_title="Count"
                    )

                    max_quality = max(max(r1['dataframe']['Individual Quality']), max(r2['dataframe']['Individual Quality'])) * 1.1
                    max_count = max(len(r1['dataframe']), len(r2['dataframe'])) * 1.1
                    
                    quality_fig.update_xaxes(range=[0, max_quality])
                    quality_fig.update_yaxes(range=[0, max_count])
                    
                    st.plotly_chart(quality_fig, use_container_width=True)

                    st.markdown("#### Seller Surplus Comparison")
                    surplus_fig = sp.make_subplots(rows=1, cols=2,
                                              shared_yaxes=True,
                                              subplot_titles=("Market 1 Seller Surplus", "Market 2 Seller Surplus"))
                    

                    surplus_fig.add_trace(
                        go.Histogram(
                            x=r1['dataframe']['Seller Surplus'],
                            name='Market 1',
                            marker_color='#1f77b4',
                            opacity=0.7
                        ),
                        row=1, col=1
                    )

                    surplus_fig.add_trace(
                        go.Histogram(
                            x=r2['dataframe']['Seller Surplus'],
                            name='Market 2',
                            marker_color='#ff7f0e',
                            opacity=0.7
                        ),
                        row=1, col=2
                    )
                    
                    surplus_fig.add_vline(
                        x=r1['dataframe']['Seller Surplus'].mean(),
                        line_dash="dash",
                        line_color="orange",
                        annotation_text=f"Avg: {r1['dataframe']['Seller Surplus'].mean():.2f}",
                        annotation_position="top right",
                        row=1, col=1
                    )
                    
                    surplus_fig.add_vline(
                        x=r2['dataframe']['Seller Surplus'].mean(),
                        line_dash="dash",
                        line_color="orange",
                        annotation_text=f"Avg: {r2['dataframe']['Seller Surplus'].mean():.2f}",
                        annotation_position="top right",
                        row=1, col=2
                    )
                    

                    surplus_fig.update_layout(
                        height=400,
                        showlegend=False,
                        bargap=0.1,
                        xaxis_title="Seller Surplus",
                        xaxis2_title="Seller Surplus",
                        yaxis_title="Count"
                    )
                    

                    max_surplus = max(max(r1['dataframe']['Seller Surplus']), max(r2['dataframe']['Seller Surplus'])) * 1.1
                    surplus_fig.update_xaxes(range=[0, max_surplus])
                    surplus_fig.update_yaxes(range=[0, max_count])
                    
                    st.plotly_chart(surplus_fig, use_container_width=True)

                    with st.expander("Market 1 Data"):
                        st.dataframe(r1['dataframe'])
                    
                    with st.expander("Market 2 Data"):
                        st.dataframe(r2['dataframe'])
        

            st.markdown("### Final Round Comparison")
            final_r1 = market1_results[0][-1]
            final_r2 = market2_results[0][-1]
            
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

elif selection == "Full Data View":
    st.title("Full Data View")
    st.markdown("""
    Compare the outcomes of different simulation setups.
    """)
    st.expander("Glossary", expanded=False).markdown("""
### Simulation Parameters
- **Starting Average Quality**: The average quality of the initial randomization of the quality of sellers (normal randomization will result in bell curve centered on this value)  
- **Quality Standard Deviation**: The standard deviation of the initial randomization of the quality of sellers from the average quality  
- **Number of Sellers**: The number of sellers along with their quality being randomized 
- **Number of Rounds**: The number of rounds to simulate in the market (each round will show the results of the previous round)

--- 

### Policy Parameters
- **Minimum Quality Standard**: The lowest acceptable quality allowed to enter the market (removes all sellers holding qualities below this value)  
- **Subsidy**: A government extra payment to sellers with a quality above the high quality threshold  
- **Penalty**: A government tax to the sellers with a quality below the low quality threshold  
- **Signaling**: Enables sellers with a quality above the high quality threshold to pay a cost to signal their high quality level to buyers who in turn pay a bonus to these sellers  
- **Signaling Cost**: Cost of acquiring the signal (think price of a college degree)  
- **Signaling Bonus**: Bonus allotted to sellers as a result of the signal (must be higher than cost to incentivize)  
- **High Quality Threshold**: Value marking any quality equal to or below as ‘high quality’  
- **Low Quality Threshold**: Value marking any quality equal to or below as ‘low quality’ 
                                                     
---
                                                     
### Insight Metrics
- **Expected Quality**: Average quality of sellers currently in the market  
- **Market Price**: Example scaled price that buyers are set to pay for a quality (in this simulation: mp = expected quality * 1000)  
- **Seller’s Valuation**: A sellers’ own valuation of their product (individual quality * 1000 without policies or signaling)  
- **Expected Payout**: The payout that the seller perceives as receiving in staying in the market (will leave if seller valuation is less than expected payout)  
- **Sells**: Whether or not the seller would stay in the market (True if seller valuation is less than or equal to expected payout)  
- **Seller Surplus**: The difference between the sellers’ valuation and the expected payout if the payout is greater than or equal to the valuation  
- **Buyer Surplus**: The difference between the sellers’ valuation and the market price  
- **Government Cost**: The cost the government incurs from penalties or subsidies  
- **Total Social Surplus**: The sum of the buyer and seller surplus minus the government cost with penalties or subsidies  
- **Penalty Amount**: The tax on the payout to sellers below the low quality threshold  
- **Subsidy Amount**: The addition to the payout to sellers above the high quality threshold  
- **High Quality**: True if individual quality is greater than or equal to high quality threshold  
- **Low Quality**: True if individual quality is less than or equal to low quality threshold  
- **Net Signaling**: Addition to the payout as a result of signaling (signaling bonus - signaling cost)
    """)
    if "round_stats" not in st.session_state:
        st.warning("Run the simulation first to view the data.")
    else:
        round_stats = st.session_state.round_stats
        if not round_stats:
            st.warning("No simulation data available.")
        else:
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

            fig1 = px.line(
                pd.DataFrame(big_metrics),
                title="Market Metrics Over Rounds",
                labels={"value": "Metric Value", "variable": "Metric"},
                markers=True
            )
            fig1.update_layout(
                xaxis_title="Round",
                yaxis_title="Value",
                height=500
            )

            fig2 = px.line(
                pd.DataFrame(small_metrics),
                title="Average Quality Over Rounds",
                labels={"value": "Average Quality", "variable": "Round"},
                markers=True
            )

            fig2.update_layout(
                xaxis_title="Round",
                yaxis_title="Average Quality",
                height=500
            )

            fig2.update_yaxes(range=[0, 1])

            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig2, use_container_width=True)



elif selection == "Insights and Analysis":
    st.title("Insights and Analysis")
    st.markdown("""
    Without proper policy implementation, asymmetric information leads to market failure over time. Expectation of quality decreases, punishing higher quality sellers and forcing them out of the market leaving less economic activity. As long as the standard deviation from the mean is above 0 (simulating quality variety), the number of sellers will decrease each round. It is for this reason that policies and signaling can be implemented within a market to attempt to keep high quality sellers from leaving.

    Use the quick simulations below to see the effects of various policy tools:
    """)
    st.markdown("---")
    st.markdown("### Basic Simulation")
    st.markdown("""
    This simulation runs with default parameters and no policies applied.
    """)
    if st.button("Run Basic Simulation"):
        with st.spinner("Running basic simulation..."):
            results = simulate_market(0.5, 100, 0.3, 5)
            st.session_state.basic_results = results
        
    if 'basic_results' in st.session_state:
        results = st.session_state.basic_results
        round_tabs = st.tabs(['Round 0'] + [f"Round {r['round']}" for r in results[0]])
        with round_tabs[0]:
            st.markdown("### Initial Seller Quality Distribution (Round 0)")
            st.plotly_chart(results[1], use_container_width=True)
        for tab, r in zip(round_tabs[1:], results[0]):
            with tab:
                st.plotly_chart(r['quality_plot'], use_container_width=True)

        round_stats = results[0]
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

        fig1 = px.line(
            pd.DataFrame(big_metrics),
            title="Market Metrics Over Rounds",
            labels={"value": "Metric Value", "variable": "Metric"},
            markers=True
        )
        fig1.update_layout(
            xaxis_title="Round",
            yaxis_title="Value",
            height=500
        )

        fig2 = px.line(
            pd.DataFrame(small_metrics),
            title="Average Quality Over Rounds",
            labels={"value": "Average Quality", "variable": "Round"},
            markers=True
        )

        fig2.update_layout(
            xaxis_title="Round",
            yaxis_title="Average Quality",
            height=500,
            yaxis=dict(
                range=[0, 1]
            )
        )

        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("""
            Without policy implementation or the possibility of signaling, the basic market will fail over time. This conclusion is independant of the initial average quality, standard deviation, or number of sellers. The market will always fail to keep high quality sellers in the market.
            """)
    st.markdown("---")
    st.markdown('### Simulation with Policies')
    st.markdown("""
                This simulation runs with all policies applied, including a minimum quality standard, subsidy for high quality sellers, and penalty for low quality sellers.
                """)
    if st.button("Run Simulation with Subsidy, Penalty, and Minimum Quality"):
        with st.spinner("Running simulation with subsidy and penalty..."):
            results = simulate_market(0.5, 100, 0.3, 5, apply_min_quality=True, min_quality=0.3, subsidy_amount=300, penalty_amount=250)
            st.session_state.policy_results = results
        
    if 'policy_results' in st.session_state:
        results = st.session_state.policy_results
        round_tabs = st.tabs(['Round 0'] + [f"Round {r['round']}" for r in results[0]])
        with round_tabs[0]:
            st.markdown("### Initial Seller Quality Distribution (Round 0)")
            st.plotly_chart(results[1], use_container_width=True)
        for tab, r in zip(round_tabs[1:], results[0]):
            with tab:
                st.plotly_chart(r['quality_plot'], use_container_width=True)
        round_stats = results[0]
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

        fig1 = px.line(
            pd.DataFrame(big_metrics),
            title="Market Metrics Over Rounds",
            labels={"value": "Metric Value", "variable": "Metric"},
            markers=True
        )
        fig1.update_layout(
            xaxis_title="Round",
            yaxis_title="Value",
            height=500
        )

        fig2 = px.line(
            pd.DataFrame(small_metrics),
            title="Average Quality Over Rounds",
            labels={"value": "Average Quality", "variable": "Round"},
            markers=True
        )

        fig2.update_layout(
            xaxis_title="Round",
            yaxis_title="Average Quality",
            height=500,
            yaxis=dict(
                range=[0, 1]
            )
        )

        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("""
                    With the implementation of a minimum quality standard, subsidy, and penalty, the market can maintain higher quality sellers over time. The subsidy incentivizes high quality sellers to remain, while the penalty discourages low quality sellers from staying in the market. The minimum quality standard ensures that only sellers above a certain quality threshold are allowed to participate.
                    """)
    st.markdown("---")
    st.markdown("### Simulation with Signaling")
    st.markdown("""
                This simulation runs with signaling enabled, allowing high quality sellers to pay a cost to signal their quality level to buyers.
                """)
    if st.button("Run Simulation with Signaling"):
        with st.spinner("Running simulation with signaling..."):
            results = simulate_market(0.5, 100, 0.3, 5, signaling_cost=50, signaling_bonus=500, high_quality_threshold=0.7)
            st.session_state.signaling_results = results
        
    if 'signaling_results' in st.session_state:
        results = st.session_state.signaling_results
        round_tabs = st.tabs(['Round 0'] + [f"Round {r['round']}" for r in results[0]])
        with round_tabs[0]:
            st.markdown("### Initial Seller Quality Distribution (Round 0)")
            st.plotly_chart(results[1], use_container_width=True)
        for tab, r in zip(round_tabs[1:], results[0]):
            with tab:
                st.plotly_chart(r['quality_plot'], use_container_width=True)
        round_stats = results[0]
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

        fig1 = px.line(
            pd.DataFrame(big_metrics),
            title="Market Metrics Over Rounds",
            labels={"value": "Metric Value", "variable": "Metric"},
            markers=True
        )
        fig1.update_layout(
            xaxis_title="Round",
            yaxis_title="Value",
            height=500
        )

        fig2 = px.line(
            pd.DataFrame(small_metrics),
            title="Average Quality Over Rounds",
            labels={"value": "Average Quality", "variable": "Round"},
            markers=True
        )

        fig2.update_layout(
            xaxis_title="Round",
            yaxis_title="Average Quality",
            height=500,
            yaxis=dict(
                range=[0, 1]
            )
        )

        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)
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
                    
    


elif selection == "Glossary":
    st.title("Glossary")
    st.markdown("""
    A brief glossary of terms used in the simulation.
                
 ### Simulation Parameters
- **Starting Average Quality**: The average quality of the initial randomization of the quality of sellers (normal randomization will result in bell curve centered on this value)  
- **Quality Standard Deviation**: The standard deviation of the initial randomization of the quality of sellers from the average quality  
- **Number of Sellers**: The number of sellers along with their quality being randomized 
- **Number of Rounds**: The number of rounds to simulate in the market (each round will show the results of the previous round)

--- 

### Policy Parameters
- **Minimum Quality Standard**: The lowest acceptable quality allowed to enter the market (removes all sellers holding qualities below this value)  
- **Subsidy**: A government extra payment to sellers with a quality above the high quality threshold  
- **Penalty**: A government tax to the sellers with a quality below the low quality threshold  
- **Signaling**: Enables sellers with a quality above the high quality threshold to pay a cost to signal their high quality level to buyers who in turn pay a bonus to these sellers  
- **Signaling Cost**: Cost of acquiring the signal (think price of a college degree)  
- **Signaling Bonus**: Bonus allotted to sellers as a result of the signal (must be higher than cost to incentivize)  
- **High Quality Threshold**: Value marking any quality equal to or below as ‘high quality’  
- **Low Quality Threshold**: Value marking any quality equal to or below as ‘low quality’  

---

### Insight Metrics
- **Expected Quality**: Average quality of sellers currently in the market  
- **Market Price**: Example scaled price that buyers are set to pay for a quality (in this simulation: mp = expected quality * 1000)  
- **Seller’s Valuation**: A sellers’ own valuation of their product (individual quality * 1000 without policies or signaling)  
- **Expected Payout**: The payout that the seller perceives as receiving in staying in the market (will leave if seller valuation is less than expected payout)  
- **Sells**: Whether or not the seller would stay in the market (True if seller valuation is less than or equal to expected payout)  
- **Seller Surplus**: The difference between the sellers’ valuation and the expected payout if the payout is greater than or equal to the valuation  
- **Buyer Surplus**: The difference between the sellers’ valuation and the market price  
- **Government Cost**: The cost the government incurs from penalties or subsidies  
- **Total Social Surplus**: The sum of the buyer and seller surplus minus the government cost with penalties or subsidies  
- **Penalty Amount**: The tax on the payout to sellers below the low quality threshold  
- **Subsidy Amount**: The addition to the payout to sellers above the high quality threshold  
- **High Quality**: True if individual quality is greater than or equal to high quality threshold  
- **Low Quality**: True if individual quality is less than or equal to low quality threshold  
- **Net Signaling**: Addition to the payout as a result of signaling (signaling bonus - signaling cost)
    """)