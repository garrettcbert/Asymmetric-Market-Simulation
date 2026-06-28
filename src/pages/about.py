import streamlit as st


def render():
    st.title("About the Simulation")
    st.markdown("""
## Introduction
This model is inspired by the work of George Akerlof, Nobel laureate in Economics and creator of the 'Akerlof's Lemons' model Akerlof's model seeks to illustrate how Asymmetric Information can lead to market failure over time in markets with quality level variety.
""")
    st.image("https://www.nobelprize.org/images/akerlof-13727-content-portrait-mobile-tiny.jpg", caption="George Akerlof, Nobel Laureate in Economics", width=200)
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
