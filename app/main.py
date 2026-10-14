from flask import Flask, jsonify, render_template, request
from app.monitor import check_services
from app.ai_investigator import investigate_incident

import time
import os
import hmac

app = Flask(__name__, template_folder="../templates")

# Demo-only simulation state shared by Gunicorn workers
# within the same container.
SERVICE_STATE_FILES = {
    "appointments": "/tmp/clinicpulse_appointments_down",
    "pharmacy": "/tmp/clinicpulse_pharmacy_down",
    "laboratory": "/tmp/clinicpulse_laboratory_down",
}

SERVICE_NAMES = {
    "appointments": "Appointment Service",
    "pharmacy": "Pharmacy Service",
    "laboratory": "Laboratory Service",
}

SERVICE_DELAYS = {
    "appointments": 0.2,
    "pharmacy": 0.3,
    "laboratory": 0.4,
}


def service_is_down(service):
    return os.path.exists(SERVICE_STATE_FILES[service])


def simulation_authorized():
    expected_token = os.environ.get("SIMULATION_TOKEN")
    provided_token = request.headers.get("X-Simulation-Token", "")

    if not expected_token:
        return False

    return hmac.compare_digest(provided_token, expected_token)


@app.route("/")
def home():
    return render_template("dashboard.html")


@app.route("/health")
def health():
    return jsonify({
        "status": "UP",
        "service": "ClinicPulse"
    })


@app.route("/services/<service>")
def service_health(service):
    if service not in SERVICE_STATE_FILES:
        return jsonify({"error": "Unknown service"}), 404

    time.sleep(SERVICE_DELAYS[service])

    if service_is_down(service):
        return jsonify({
            "service": SERVICE_NAMES[service],
            "status": "DOWN",
            "message": "Simulated service outage"
        }), 503

    return jsonify({
        "service": SERVICE_NAMES[service],
        "status": "UP"
    })


@app.route("/api/status")
def service_status():
    return jsonify(check_services())


@app.route("/simulate/<service>/<action>", methods=["POST"])
def simulate_service(service, action):
    if not simulation_authorized():
        return jsonify({"error": "Forbidden"}), 403

    if service not in SERVICE_STATE_FILES:
        return jsonify({"error": "Unknown service"}), 404

    if action not in ("down", "up"):
        return jsonify({"error": "Unknown simulation action"}), 404

    state_file = SERVICE_STATE_FILES[service]

    if action == "down":
        with open(state_file, "w"):
            pass

        return jsonify({
            "message": f"{SERVICE_NAMES[service]} failure simulation activated"
        })

    if os.path.exists(state_file):
        os.remove(state_file)

    return jsonify({
        "message": f"{SERVICE_NAMES[service]} restored"
    })


@app.route("/api/investigate", methods=["POST"])
def investigate():
    if not simulation_authorized():
        return jsonify({"error": "Forbidden"}), 403

    services = check_services()

    failed_services = [
        service for service in services
        if service["status"] == "DOWN"
    ]

    if not failed_services:
        return jsonify({
            "message": "All services are healthy. No incident detected."
        })

    investigations = []

    for service in failed_services:
        try:
            report = investigate_incident(
                service_name=service["service"],
                status=service["status"],
                response_time_ms=service["response_time_ms"]
            )

            investigations.append({
                "service": service["service"],
                "status": service["status"],
                "ai_report": report
            })

        except Exception:
            app.logger.exception("AI investigation failed")

            return jsonify({
                "error": "AI investigation temporarily unavailable"
            }), 503

    return jsonify({
        "incident_count": len(investigations),
        "investigations": investigations
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
