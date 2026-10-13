from flask import Flask, jsonify, render_template, request
from app.monitor import check_services
import time
import os
import hmac

app = Flask(__name__, template_folder="../templates")

pharmacy_failure = False

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

    if pharmacy_failure:
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
    global pharmacy_failure

    if not simulation_authorized():
        return jsonify({"error": "Forbidden"}), 403

    pharmacy_failure = True

    return jsonify({
        "message": "Pharmacy failure simulation activated"
    })


@app.route("/simulate/pharmacy/up", methods=["POST"])
def simulate_pharmacy_up():
    global pharmacy_failure

    if not simulation_authorized():
        return jsonify({"error": "Forbidden"}), 403

    pharmacy_failure = False

    return jsonify({
        "message": "Pharmacy service restored"
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
