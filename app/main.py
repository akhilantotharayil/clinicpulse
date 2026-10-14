from flask import Flask, jsonify, render_template, request
from app.monitor import check_services
from app.ai_investigator import investigate_incident

import time
import os
import hmac

app = Flask(__name__, template_folder="../templates")

# Shared simulation state across Gunicorn workers
PHARMACY_STATE_FILE = "/tmp/clinicpulse_pharmacy_down"


def pharmacy_is_down():
    return os.path.exists(PHARMACY_STATE_FILE)


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


@app.route("/services/appointments")
def appointments():
    time.sleep(0.2)

    return jsonify({
        "service": "Appointment Service",
        "status": "UP"
    })


@app.route("/services/pharmacy")
def pharmacy():
    time.sleep(0.3)

    if pharmacy_is_down():
        return jsonify({
            "service": "Pharmacy Service",
            "status": "DOWN",
            "message": "Simulated service outage"
        }), 503

    return jsonify({
        "service": "Pharmacy Service",
        "status": "UP"
    })


@app.route("/services/laboratory")
def laboratory():
    time.sleep(0.4)

    return jsonify({
        "service": "Laboratory Service",
        "status": "UP"
    })


@app.route("/api/status")
def service_status():
    return jsonify(check_services())


@app.route("/simulate/pharmacy/down", methods=["POST"])
def simulate_pharmacy_down():
    if not simulation_authorized():
        return jsonify({"error": "Forbidden"}), 403

    with open(PHARMACY_STATE_FILE, "w"):
        pass

    return jsonify({
        "message": "Pharmacy failure simulation activated"
    })


@app.route("/simulate/pharmacy/up", methods=["POST"])
def simulate_pharmacy_up():
    if not simulation_authorized():
        return jsonify({"error": "Forbidden"}), 403

    if os.path.exists(PHARMACY_STATE_FILE):
        os.remove(PHARMACY_STATE_FILE)

    return jsonify({
        "message": "Pharmacy service restored"
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
