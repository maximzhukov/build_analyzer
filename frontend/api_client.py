import requests
import os
import streamlit as st


API_URL = os.getenv("API_URL", "http://localhost:8000")

def upload_plan_csv(project_id: int, file_buffer):
    try:
        files = {"file": ("plan.csv", file_buffer, "text/csv")}
        response = requests.post(f"{API_URL}/projects/{project_id}/upload-plan/", files=files)
        response.raise_for_status()
        
        st.cache_data.clear() 
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка при загрузке плана: {e}")
        return False
    
def update_stage_mapping(stage_id: int, nlp_stage_id: str):
    try:
        response = requests.post(
            f"{API_URL}/stages/{stage_id}/mapping",
            json={"nlp_stage_id": nlp_stage_id}
        )
        response.raise_for_status()
        
        st.cache_data.clear() 
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка сохранения маппинга: {e}")
        return False
    
@st.cache_data(ttl=5) 
def get_project_data(project_id: int):
    try:
        response = requests.get(f"{API_URL}/projects/{project_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Ошибка подключения к Backend API: {e}")
        return None