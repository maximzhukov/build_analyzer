import os
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta
from api_client import get_project_data
from gantt_component import render_custom_gantt
from media_utils import generate_timelapse
from config import ANNOTATED_DIR, TIMELAPSE_PATH

API_BASE_URL = os.getenv("API_URL", "http://backend:8000")

def render_timelapse(path):
    if not os.path.exists(path):
        st.error("Таймлапс еще не создан")
        return
    st.video(path, autoplay=True, loop=True, muted=True)

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
            try:
                resp = requests.get(f"{API_BASE_URL}/stages/{stage_id}/history", timeout=5)
                history_resp = resp.json() if resp.status_code == 200 else {}
            except:
                history_resp = {}

            # ЕСЛИ СЕГОДНЯ НЕ БЫЛО АКТИВНОСТИ - СКРЫВАЕМ ЭТАП
            if not history_resp.get("has_today_activity"):
                continue

            chart_data = history_resp.get("chart_data", [])
            start_vol = history_resp.get("today_start_vol", 0)
            end_vol = history_resp.get("today_end_vol", 0)
            today_pct = ((end_vol - start_vol) / target * 100) if target > 0 else 0

            active_details.append({
                "id": stage_id,
                "name": name,
                "total_volume": target,
                "current_volume": current,
                "cumulative_progress": round(progress_pct, 1),
                "today_percent": round(today_pct, 1), 
                "chart_data": chart_data,
                "today_increment": end_vol - start_vol
            })

    project_status = "Частично отстает от графика" if delays else "В графике"

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Статус проекта", value=project_status)
    st.markdown("---")

    if active_details:
        st.info("Активности:")
        st.markdown("<br>", unsafe_allow_html=True)
        
        for i, activity in enumerate(active_details, 1):
            col_num, col_content = st.columns([0.05, 0.95])
            
            with col_num:
                st.markdown(f"### {i}.")
                
            with col_content:
                st.dataframe(
                    pd.DataFrame([{
                        "Этап": activity["name"],
                        "Выполнено всего": f"{activity['cumulative_progress']}%",
                        "Прирост за сегодня": f"+ {activity['today_percent']}%",
                    }]),
                    hide_index=True,
                    use_container_width=True,
                )
                
                chart_data = activity["chart_data"]
                if chart_data:
                    chart_df = pd.DataFrame(chart_data)
                    chart_df["time"] = pd.to_datetime(chart_df["time"], format='ISO8601')
                    fig = px.line(
                        chart_df, x="time", y="volume", 
                        title="Динамика объема работ:",
                        markers=True, line_shape="hv"
                    )
                    fig.update_traces(line_color="#FF9F1C", line_width=3)
                    fig.update_layout(height=280, margin=dict(l=0, r=0, t=40, b=0), xaxis_title="Дата и время", yaxis_title="Объем (м3)")
                    # Настраиваем красивый формат оси X (день.месяц Часы:Минуты)
                    fig.update_xaxes(tickformat="%d.%m\n%H:%M")
                    
                    st.plotly_chart(fig, use_container_width=True)

                    speed_per_day = activity["today_increment"] if activity["today_increment"] > 0 else activity["current_volume"]
                    
                    remaining_volume = activity["total_volume"] - activity["current_volume"]
                    if speed_per_day > 0 and remaining_volume > 0:
                        days_left = remaining_volume / speed_per_day
                        eta_date = today + timedelta(days=round(days_left))
                        st.info(
                            f"**Прогноз:** При текущем темпе этап завершится "
                            f"**{eta_date.strftime('%d.%m.%Y')}** (осталось ~{round(days_left)} дн.)"
                        )
                    
            st.markdown("<hr style='margin-top: 2rem; margin-bottom: 2rem; border-top: 1px dashed #ccc;'>", unsafe_allow_html=True)
    else:
        st.info("Ожидание видеопотока. Сегодня активность техники еще не зафиксирована...")

    st.subheader("График производства работ (Диаграмма Ганта)")
    render_custom_gantt(stages, height=480)
    st.markdown("---")

    if delays:
        st.error("Отставания:")
        st.dataframe(
            pd.DataFrame(delays).rename(columns={"name": "Название этапа", "days": "Дней просрочки"}),
            hide_index=True,
            use_container_width=True
        )
    st.markdown("---")
    st.subheader("Визуальный контроль")
    if "active_media" not in st.session_state:
        st.session_state.active_media = "live"

    col_media, col_controls = st.columns([3, 2])

    with col_media:
        if st.session_state.active_media == "timelapse":
            with st.spinner("Склеиваем кадры за сегодня... (занимает ~5 секунд)"):
                success = generate_timelapse(input_folder=ANNOTATED_DIR, output_file=TIMELAPSE_PATH)
                if success:
                    st.success("Таймлапс успешно сгенерирован!")
                    render_timelapse(TIMELAPSE_PATH)
                else:
                    st.error("Не найдены кадры в папке (проверьте наличие demo_frames).")
        else:
            st.info("Ожидание видеопотока с камеры (LIVE)...")

    with col_controls:
        is_timelapse_active = st.session_state.active_media == "timelapse"
        is_live_active = st.session_state.active_media == "live"

        if st.button("Таймлапс с начала дня", use_container_width=True, type="primary" if is_timelapse_active else "secondary"):
            st.session_state.active_media = "timelapse"
            st.rerun()
            
        if st.button("Трансляция", use_container_width=True, type="primary" if is_live_active else "secondary"):
            st.session_state.active_media = "live"
            st.rerun()