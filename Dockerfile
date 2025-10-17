# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY .env.prod .env

# Create non-root user (security best practice)
RUN useradd -m appuser
USER appuser

EXPOSE 8503

# HEALTHCHECK CMD curl --fail http://localhost:8503/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "Scripts/strmlt.py", "--server.port=8503" ]
#/venv/bin/streamlit run Scripts/strmlt.py --server.port 8503
