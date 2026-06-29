# Asymmetric Market Simulation

An interactive simulation of George Akerlof's "Market for Lemons" model, demonstrating how asymmetric information leads to market failure over time. Built with Streamlit.

Try the live simulation [here](https://asym-market-simulation-cat4sztwhnhsaxkmgspjwr.streamlit.app/).

## Overview

In a market with asymmetric information, only sellers know the true quality of their product. Buyers, unable to distinguish quality, pay based on the expected average which drives high-quality sellers out of the market over time. This simulation lets you observe that dynamic and experiment with policy interventions to counteract it.

## Features

- **Market Simulation** - Customize starting quality, number of sellers, standard deviation, and number of rounds
- **Policy Tools** - Apply minimum quality standards, subsidies, penalties, and signaling to stabilize the market
- **Policy Comparisons** - Run two markets side-by-side with different policy settings
- **Full Data View** - Inspect per-round seller data and aggregate metrics
- **Insights & Analysis** - Pre-configured simulations illustrating key outcomes

## Project Structure

```
app.py                  # Entry point
src/
  simulation.py         # Market simulation logic
  pages/
    about.py
    market_simulation.py
    policy_comparisons.py
    full_data_view.py
    insights.py
    glossary.py
```

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Dependencies

- [Streamlit](https://streamlit.io/) - UI framework
- [Plotly](https://plotly.com/python/) - Interactive charts
- [NumPy](https://numpy.org/) / [Pandas](https://pandas.pydata.org/) - Simulation data processing
