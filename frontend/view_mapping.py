import streamlit as st
import pandas as pd
from api_client import get_project_data

def render_mapping(project_id: int):
    data = get_project_data(project_id)
    
    if not data or not data.get("stages"):
        st.info("Файл плана не найден. Пожалуйста, загрузите CSV вручную через боковое меню.")
        return

    
    st.success("Загружен базовый план")
    
    st.subheader("План производства работ")
    
    stages = data["stages"]
    
    
    formatted_stages = []
    for stage in stages:
        
        vol_str = str(stage["target_volume"])
            
        formatted_stages.append({
            "Наименование работ": stage["name"],
            "Начало": pd.to_datetime(stage.get("start_date")).strftime("%Y-%m-%d") if stage.get("start_date") else "-",
            "Окончание": pd.to_datetime(stage.get("end_date")).strftime("%Y-%m-%d") if stage.get("end_date") else "-",
            "Объем": vol_str,
        })
        
    df = pd.DataFrame(formatted_stages)

    
    st.dataframe(
        df,
        column_order=["Наименование работ", "Начало", "Окончание", "Объем"],
        hide_index=True,
        use_container_width=True
    )