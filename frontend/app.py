
import streamlit as st
from view_dashboard import render_dashboard
from view_mapping import render_mapping

st.set_page_config(page_title="BuilderCV", layout="wide")

PROJECT_ID = 1

st.title("🏗️ BuilderCV Platform")


tab_dashboard, tab_mapping = st.tabs(["Дашборд аналитики", "Маппинг этапов (NLP)"])

with tab_dashboard:
    render_dashboard(PROJECT_ID)

with tab_mapping:
    render_mapping(PROJECT_ID)