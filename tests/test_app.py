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


def test_pharmacy_failure_and_recovery():
    client = app.test_client()

    try:
        # Simulate pharmacy failure
        response = client.post("/simulate/pharmacy/down")
        assert response.status_code == 200

        # Verify pharmacy is unavailable
        response = client.get("/services/pharmacy")
        assert response.status_code == 503
        assert response.get_json()["status"] == "DOWN"

    finally:
        # Always restore pharmacy, even if an assertion fails
        client.post("/simulate/pharmacy/up")

    # Verify recovery
    response = client.get("/services/pharmacy")
    assert response.status_code == 200
    assert response.get_json()["status"] == "UP"
