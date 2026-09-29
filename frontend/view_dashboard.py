import streamlit as st
import pandas as pd
from api_client import get_project_data

def render_dashboard(project_id: int):
    st.header("🎛️ Дашборд аналитики объекта")
    
    data = get_project_data(project_id)
    if not data or not data.get("stages"):
        st.info("Нет данных для отображения аналитики.")
        return

    stages = data["stages"]
    
    
    total_target = sum(s["target_volume"] for s in stages)
    total_current = sum(s["current_volume"] for s in stages)
    overall_progress = (total_current / total_target * 100) if total_target > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Всего этапов", len(stages))
    col2.metric("Общий плановый объем", f"{total_target:.1f}")
    col3.metric("Общий прогресс", f"{overall_progress:.1f}%")
    
    st.divider()

    
    st.subheader("📊 Выполнение по типам работ")
    
    
    df_chart = pd.DataFrame(stages)
    if not df_chart.empty:
        
        df_chart['Процент (%)'] = (df_chart['current_volume'] / df_chart['target_volume'] * 100).fillna(0)
        
        df_chart['Процент (%)'] = df_chart['Процент (%)'].apply(lambda x: min(x, 100.0))
        
        st.bar_chart(
            data=df_chart,
            x='name',
            y='Процент (%)',
            use_container_width=True
        )