import requests
import time
import os

BASE_URL = os.getenv("MONITOR_BASE_URL", "http://127.0.0.1:5000")

SERVICES = {
    "Appointment Service": f"{BASE_URL}/services/appointments",
    "Pharmacy Service": f"{BASE_URL}/services/pharmacy",
    "Laboratory Service": f"{BASE_URL}/services/laboratory"
}


def check_services():
    results = []

    for service_name, url in SERVICES.items():
        start_time = time.perf_counter()

        try:
            response = requests.get(url, timeout=3)

            response_time = round(
                (time.perf_counter() - start_time) * 1000, 2
            )

            status = "UP" if response.status_code == 200 else "DOWN"

        except requests.RequestException:
            response_time = None
            status = "DOWN"

        results.append({
            "service": service_name,
            "status": status,
            "response_time_ms": response_time
        })

    return results
