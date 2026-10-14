#!/bin/sh
set -eu

echo "Starting ClinicPulse application..."

gunicorn --bind 0.0.0.0:8000 --workers 2 --threads 4 app.main:app &
APP_PID=$!

cleanup() {
    echo "Stopping ClinicPulse..."
    kill "$APP_PID" 2>/dev/null || true

    if [ -n "${MONITOR_PID:-}" ]; then
        kill "$MONITOR_PID" 2>/dev/null || true
        wait "$MONITOR_PID" 2>/dev/null || true
    fi

    wait "$APP_PID" 2>/dev/null || true
}

trap cleanup TERM INT

echo "Waiting for ClinicPulse to become healthy..."

READY=0

for attempt in $(seq 1 30); do
    if ! kill -0 "$APP_PID" 2>/dev/null; then
        echo "Gunicorn exited during startup"
        wait "$APP_PID" || true
        exit 1
    fi

    if python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)" >/dev/null 2>&1; then
        READY=1
        break
    fi

    sleep 1
done

if [ "$READY" -ne 1 ]; then
    echo "ClinicPulse failed to become healthy"
    cleanup
    exit 1
fi

echo "ClinicPulse is healthy. Starting CloudWatch monitor..."

python -m app.monitor &
MONITOR_PID=$!

wait "$APP_PID" || true
cleanup
exit 0
