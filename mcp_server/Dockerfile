FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install debugpy

COPY . /app

EXPOSE 8765
EXPOSE 5679

CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5679", "--wait-for-client", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8765", "--reload"]
