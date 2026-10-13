import requests
import time
import os
import boto3

BASE_URL = os.getenv("MONITOR_BASE_URL", "http://127.0.0.1:8000")

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

def publish_cloudwatch_metrics():
    cloudwatch = boto3.client("cloudwatch", region_name="us-east-1")

    results = check_services()

    metric_data = []

    for result in results:
        service_name = result["service"]
        status = result["status"]

        health_value = 1 if status == "UP" else 0

        metric_data.append({
            "MetricName": "ServiceHealth",
            "Dimensions": [
                {
                    "Name": "Service",
                    "Value": service_name
                },
                {
                    "Name": "Environment",
                    "Value": "clinicpulse-blue"
                }
            ],
            "Value": health_value,
            "Unit": "Count"
        })

        print(f"{service_name}: {status} → CloudWatch value: {health_value}")

    cloudwatch.put_metric_data(
        Namespace="ClinicPulse",
        MetricData=metric_data
    )

    print("CloudWatch metrics published successfully")

if __name__ == "__main__":
    print("ClinicPulse CloudWatch monitor started")

    while True:
        try:
            publish_cloudwatch_metrics()
        except Exception as error:
            print(f"CloudWatch monitoring error: {error}", flush=True)

        time.sleep(60)
