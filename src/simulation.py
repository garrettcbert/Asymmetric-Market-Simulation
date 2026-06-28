import numpy as np
from math import floor
import pandas as pd
import plotly.graph_objects as go


def simulate_market(avg_quality, num_sellers, std_quality, num_rounds, apply_min_quality=False, min_quality=0,
                    subsidy_amount=0, penalty_amount=0, signaling_cost=0, signaling_bonus=0, high_quality_threshold=0.7, low_quality_threshold=0.3):

    warnings = []

    initial_quality = np.clip(np.random.normal(avg_quality, std_quality, num_sellers), 0, 1)
    if apply_min_quality:
        initial_quality[initial_quality < min_quality] = np.nan
        initial_quality = initial_quality[~np.isnan(initial_quality)]
        num_sellers = len(initial_quality)
        if num_sellers == 0:
            return None, None, ["No sellers meet the minimum quality standard. Simulation ends early."]

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

        exp_payout = np.full(len(old_quality), market_price, dtype=float) + np.where(signals_sent, signaling_bonus, 0) - np.where(signals_sent, signaling_cost, 0)

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
            warnings.append(f"Simulation ended early at Round {round_num}: no sellers remain. Rounds stop because there are no more sellers able to participate in the market.")
            break

        sellers = pd.DataFrame({
            'Individual Quality': old_quality,
            'Expected Quality': expected_quality,
            'Market Price': market_price,
            'Seller Valuation': seller_values,
            'Expected Payout': exp_payout,
            'Sells': sales,
            'Seller Surplus': np.where(sales, exp_payout - seller_values, 0),
            'Buyer Surplus': np.where(sales, seller_values - market_price, 0),
            'Total Social Surplus': np.where(sales, exp_payout - seller_values, 0) + np.where(sales, seller_values - market_price, 0) - gov_cost,
            'Penalty Amount': penalty_amount,
            'Subsidy Amount': subsidy_amount,
            'Government Cost': gov_cost,
            'High Quality': np.where(old_quality > high_quality_threshold, True, False),
            'Low Quality': np.where(old_quality < low_quality_threshold, True, False),
            'Net Signaling': np.where(signals_sent, signaling_bonus - signaling_cost, 0)
        })

        remaining_sellers = sellers[sellers['Sells']]
        num_sales = len(remaining_sellers)

        if num_sales == 0:
            warnings.append("No sellers were able to sell. Simulation ends early.")
            break
        if avg_quality == 0:
            warnings.append("Average quality is 0. Simulation ends early.")
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
        surplus_fig.add_trace(go.Histogram(
            x=sellers['Buyer Surplus'],
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
            x=sellers['Buyer Surplus'].sum() + sellers['Seller Surplus'].sum() - sellers['Government Cost'].sum(),
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
            'dataframe': sellers
        })

    return round_stats, fig0, warnings
