FROM python:3.10-slim

WORKDIR /app

RUN pip install streamlit pandas requests plotly opencv-python-headless

COPY ./frontend /app/frontend

WORKDIR /app/frontend

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]