FROM python:3.10-slim

WORKDIR /app

RUN pip install fastapi uvicorn sqlalchemy pydantic psycopg2-binary python-multipart

COPY ./backend /app/backend
COPY ./workers /app/workers

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]