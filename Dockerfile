FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY survival.py .

CMD ["python", "survival.py"]
