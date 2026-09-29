import streamlit as st
import pandas as pd
from api_client import get_project_data, update_stage_mapping


AVAILABLE_NLP_STAGES = [
    "STAGE_EARTH_WORK", 
    "STAGE_FOUNDATION", 
    "STAGE_BRICK_WORK", 
    "STAGE_ROOFING", 
    "UNKNOWN"
]

def render_mapping(project_id: int):
    st.header("🔗 Маппинг этапов (NLP Validation)")
    st.write("Проверьте, как система распознала названия работ из загруженного плана.")

    data = get_project_data(project_id)
    if not data or not data.get("stages"):
        st.info("Загрузите план-график, чтобы начать маппинг.")
        return

    stages = data["stages"]

    
    for stage in stages:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            
            col1.text_input(
                "Название из Плана (CSV)", 
                value=stage["name"], 
                disabled=True, 
                key=f"name_{stage['id']}"
            )
            
            
            current_mapping = stage["nlp_stage_id"] if stage["nlp_stage_id"] in AVAILABLE_NLP_STAGES else "UNKNOWN"
            current_index = AVAILABLE_NLP_STAGES.index(current_mapping)
            
            selected_nlp_id = col2.selectbox(
                "Распознанный Этап (Система)", 
                options=AVAILABLE_NLP_STAGES, 
                index=current_index,
                key=f"nlp_{stage['id']}"
            )
            
            
            with col3:
                st.write("") 
                st.write("")
                if selected_nlp_id != current_mapping:
                    if st.button("Сохранить", key=f"btn_{stage['id']}"):
                        success = update_stage_mapping(stage["id"], selected_nlp_id)
                        if success:
                            st.success("Обновлено!")
                            st.rerun() 
            st.divider()