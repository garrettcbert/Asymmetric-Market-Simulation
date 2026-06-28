import streamlit as st

GLOSSARY_MARKDOWN = """
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
- **High Quality Threshold**: Value marking any quality equal to or below as 'high quality'
- **Low Quality Threshold**: Value marking any quality equal to or below as 'low quality'

---

### Insight Metrics
- **Expected Quality**: Average quality of sellers currently in the market
- **Market Price**: Example scaled price that buyers are set to pay for a quality (in this simulation: mp = expected quality * 1000)
- **Seller's Valuation**: A sellers' own valuation of their product (individual quality * 1000 without policies or signaling)
- **Expected Payout**: The payout that the seller perceives as receiving in staying in the market (will leave if seller valuation is less than expected payout)
- **Sells**: Whether or not the seller would stay in the market (True if seller valuation is less than or equal to expected payout)
- **Seller Surplus**: The difference between the sellers' valuation and the expected payout if the payout is greater than or equal to the valuation
- **Buyer Surplus**: The difference between the sellers' valuation and the market price
- **Government Cost**: The cost the government incurs from penalties or subsidies
- **Total Social Surplus**: The sum of the buyer and seller surplus minus the government cost with penalties or subsidies
- **Penalty Amount**: The tax on the payout to sellers below the low quality threshold
- **Subsidy Amount**: The addition to the payout to sellers above the high quality threshold
- **High Quality**: True if individual quality is greater than or equal to high quality threshold
- **Low Quality**: True if individual quality is less than or equal to low quality threshold
- **Net Signaling**: Addition to the payout as a result of signaling (signaling bonus - signaling cost)
"""


def render():
    st.title("Glossary")
    st.markdown("A brief glossary of terms used in the simulation.")
    st.markdown(GLOSSARY_MARKDOWN)


def expander(label="Glossary"):
    st.expander(label, expanded=False).markdown(GLOSSARY_MARKDOWN)
