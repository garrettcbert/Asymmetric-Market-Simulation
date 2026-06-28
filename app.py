import streamlit as st

from src.pages.about import render as render_about
from src.pages.market_simulation import render as render_market_simulation
from src.pages.policy_comparisons import render as render_policy_comparisons
from src.pages.full_data_view import render as render_full_data_view
from src.pages.insights import render as render_insights
from src.pages.glossary import render as render_glossary

st.set_page_config(page_title="Asymmetric Information Market Simulation", layout="wide")
st.sidebar.title("Asymmetric Information Market Simulation")
st.sidebar.markdown("Select a section to explore the simulation and its insights.")
selection = st.sidebar.radio("Go to", ["About", "Market Simulation", "Policy Comparisons", "Full Data View", "Insights and Analysis", "Glossary"])

pages = {
    "About": render_about,
    "Market Simulation": render_market_simulation,
    "Policy Comparisons": render_policy_comparisons,
    "Full Data View": render_full_data_view,
    "Insights and Analysis": render_insights,
    "Glossary": render_glossary,
}

pages[selection]()
