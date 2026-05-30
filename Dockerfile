FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY shazam_requirements.txt ./
RUN pip install --no-cache-dir -r shazam_requirements.txt

COPY shazam_server.py ./
COPY shazam.html ./
COPY style.css ./
COPY script.js ./

EXPOSE 8000

# Railway injects $PORT. Default to 8000 for local docker run.
CMD ["sh", "-c", "exec uvicorn shazam_server:app --host 0.0.0.0 --port ${PORT:-8000}"]
