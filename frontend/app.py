
import streamlit as st
from view_dashboard import render_dashboard
from view_mapping import render_mapping
from api_client import get_project_data, upload_plan_csv

st.set_page_config(page_title="BuilderCV", layout="wide")

PROJECT_ID = 1

with st.sidebar:
    st.header("Управление проектом")
    st.subheader("Загрузка плана-графика")
    
    uploaded_file = st.file_uploader("Выберите план (CSV файл)", type=["csv"])
    
    if uploaded_file is not None:
        if st.button("Отправить и запустить NLP"):
            with st.spinner("Загрузка и обработка..."):
                success = upload_plan_csv(PROJECT_ID, uploaded_file)
                if success:
                    st.success("План загружен! NLP-модель начала маппинг.")
                    st.rerun()

st.title("BuilderCV Platform")


tab_dashboard, tab_mapping = st.tabs(["Сводка", "План"])

with tab_dashboard:
    render_dashboard(PROJECT_ID)

with tab_mapping:
    render_mapping(PROJECT_ID)