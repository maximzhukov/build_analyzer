import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
from api_client import get_project_data
from gantt_component import render_custom_gantt  

API_BASE_URL = "http://backend:8000"

def render_dashboard(project_id: int):
    st.header("Сводка за текущий день")
    
    data = get_project_data(project_id)
    if not data or not data.get("stages"):
        st.warning("Сначала загрузите план через боковое меню.")
        return

    stages = data["stages"]
    today = datetime.now()

    delays = []
    active_details = []

    for stage in stages:
        name = stage["name"]
        stage_id = stage["id"]
        target = stage["target_volume"]
        current = stage["current_volume"]
        
        end_dt = pd.to_datetime(stage.get("end_date")) if stage.get("end_date") else today
        progress_pct = (current / target * 100) if target > 0 else 0
        
        if end_dt < today and progress_pct < 100:
            delay_days = (today - end_dt).days
            if delay_days > 0:
                delays.append({"name": name, "days": delay_days})

        
        if 0 < progress_pct < 100:
            active_details.append({
                "id": stage_id,
                "name": name,
                "total_volume": target,
                "current_volume": current,
                "cumulative_progress": round(progress_pct, 1),
                "today_percent": round(progress_pct, 1), 
            })

    project_status = "Частично отстает от графика" if delays else "В графике"

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Статус проекта", value=project_status)
    st.markdown("---")

    if active_details:
        st.info("Активные этапы:")
        st.markdown("<br>", unsafe_allow_html=True)
        
        for i, activity in enumerate(active_details, 1):
            col_num, col_content = st.columns([0.05, 0.95])
            
            with col_num:
                st.markdown(f"##
                
            with col_content:
                st.dataframe(
                    pd.DataFrame([{
                        "Этап": activity["name"],
                        "Выполнено всего": f"{activity['cumulative_progress']}%",
                        "Объем за сегодня": f"{activity['today_percent']}%",
                    }]),
                    hide_index=True,
                    use_container_width=True,
                )
                
                try:
                    resp = requests.get(f"{API_BASE_URL}/stages/{activity['id']}/history", timeout=5)
                    history_data = resp.json() if resp.status_code == 200 else []
                except:
                    history_data = []

                if history_data:
                    chart_data = pd.DataFrame(history_data)
                    fig = px.line(
                        chart_data, x="time", y="volume", 
                        title="Динамика объема работ (real-time)",
                        markers=True, line_shape="hv"
                    )
                    fig.update_traces(line_color="#FF9F1C", line_width=3)
                    fig.update_layout(height=250, margin=dict(l=0, r=0, t=40, b=0), xaxis_title="Время", yaxis_title="Объем (м3)")
                    st.plotly_chart(fig, use_container_width=True)

                    remaining_volume = activity["total_volume"] - activity["current_volume"]
                    if activity["current_volume"] > 0 and remaining_volume > 0:
                        days_left = remaining_volume / activity["current_volume"]
                        eta_date = today + timedelta(days=round(days_left))
                        st.info(
                            f"**Прогноз:** При текущем темпе этап завершится "
                            f"**{eta_date.strftime('%d.%m.%Y')}** (осталось ~{round(days_left)} дн.)"
                        )
                else:
                    st.info("Ожидание прибытия самосвалов для построения графика...")
                    
            st.markdown("<hr style='margin-top: 2rem; margin-bottom: 2rem; border-top: 1px dashed #ccc;'>", unsafe_allow_html=True)
    else:
        st.info("Сегодня не выявлено активных этапов")

    
    st.subheader("График производства работ (Диаграмма Ганта)")
    render_custom_gantt(stages, height=480)
    st.markdown("---")
    
    
    st.subheader("Визуальный контроль")
    if "active_media" not in st.session_state:
        st.session_state.active_media = "live"

    col_media, col_controls = st.columns([3, 2])

    with col_media:
        st.info(f"Отображение режима: {st.session_state.active_media.upper()}")

    with col_controls:
        is_timelapse_active = st.session_state.active_media == "timelapse"
        is_live_active = st.session_state.active_media == "live"

        if st.button("Таймлапс с начала дня", use_container_width=True, type="primary" if is_timelapse_active else "secondary"):
            st.session_state.active_media = "timelapse"
            st.rerun()
            
        if st.button("Трансляция", use_container_width=True, type="primary" if is_live_active else "secondary"):
            st.session_state.active_media = "live"
            st.rerun()