# Stage 1: Install Python dependencies
FROM python:3.14-slim AS builder

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: Runtime
FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY app/ ./app/
COPY templates/ ./templates/
COPY static/ ./static/

RUN useradd --create-home --uid 10001 clinicpulse

USER clinicpulse

ENV MONITOR_BASE_URL=http://127.0.0.1:8000
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "app.main:app"]
