FROM python:3.12-slim

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

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn shazam_server:app --host 0.0.0.0 --port ${PORT:-8000}"]
