from app.main import app


def test_health_endpoint():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "UP"
    assert data["service"] == "ClinicPulse"


def test_appointments_service():
    client = app.test_client()

    response = client.get("/services/appointments")

    assert response.status_code == 200
    assert response.get_json()["status"] == "UP"


def test_pharmacy_service():
    client = app.test_client()

    response = client.get("/services/pharmacy")

    assert response.status_code == 200
    assert response.get_json()["status"] == "UP"


def test_laboratory_service():
    client = app.test_client()

    response = client.get("/services/laboratory")

    assert response.status_code == 200
    assert response.get_json()["status"] == "UP"


def test_pharmacy_failure_and_recovery(monkeypatch):
    client = app.test_client()

    monkeypatch.setenv("SIMULATION_TOKEN", "test-secret-token")

    headers = {
        "X-Simulation-Token": "test-secret-token"
    }

    try:
        response = client.post(
            "/simulate/pharmacy/down",
            headers=headers
        )

        assert response.status_code == 200

        response = client.get("/services/pharmacy")

        assert response.status_code == 503
        assert response.get_json()["status"] == "DOWN"

    finally:
        response = client.post(
            "/simulate/pharmacy/up",
            headers=headers
        )
        assert response.status_code == 200

    response = client.get("/services/pharmacy")

    assert response.status_code == 200
    assert response.get_json()["status"] == "UP"


def test_simulation_rejects_wrong_token(monkeypatch):
    client = app.test_client()

    monkeypatch.setenv("SIMULATION_TOKEN", "test-secret-token")

    response = client.post(
        "/simulate/pharmacy/down",
        headers={"X-Simulation-Token": "wrong-token"}
    )

    assert response.status_code == 403


def test_simulation_rejects_missing_token(monkeypatch):
    client = app.test_client()

    monkeypatch.setenv("SIMULATION_TOKEN", "test-secret-token")

    response = client.post("/simulate/pharmacy/down")

    assert response.status_code == 403


def test_simulation_rejects_unconfigured_token(monkeypatch):
    client = app.test_client()

    monkeypatch.delenv("SIMULATION_TOKEN", raising=False)

    response = client.post(
        "/simulate/pharmacy/down",
        headers={"X-Simulation-Token": "any-token"}
    )

    assert response.status_code == 403
