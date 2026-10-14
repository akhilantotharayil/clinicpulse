import pytest

from app.main import app, SERVICE_STATE_FILES


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("SIMULATION_TOKEN", "test-secret-token")

    for service in SERVICE_STATE_FILES:
        monkeypatch.setitem(
            SERVICE_STATE_FILES,
            service,
            str(tmp_path / f"{service}_down")
        )

    with app.test_client() as test_client:
        yield test_client


HEADERS = {
    "X-Simulation-Token": "test-secret-token"
}


@pytest.mark.parametrize("service", [
    "appointments",
    "pharmacy",
    "laboratory"
])
def test_independent_failure_and_recovery(client, service):
    response = client.post(
        f"/simulate/{service}/down",
        headers=HEADERS
    )
    assert response.status_code == 200

    response = client.get(f"/services/{service}")
    assert response.status_code == 503
    assert response.get_json()["status"] == "DOWN"

    response = client.post(
        f"/simulate/{service}/up",
        headers=HEADERS
    )
    assert response.status_code == 200

    response = client.get(f"/services/{service}")
    assert response.status_code == 200
    assert response.get_json()["status"] == "UP"


def test_simultaneous_failures(client):
    for service in ("appointments", "laboratory"):
        response = client.post(
            f"/simulate/{service}/down",
            headers=HEADERS
        )
        assert response.status_code == 200

    for service in ("appointments", "laboratory"):
        response = client.get(f"/services/{service}")
        assert response.status_code == 503
        assert response.get_json()["status"] == "DOWN"

    response = client.get("/services/pharmacy")
    assert response.status_code == 200
    assert response.get_json()["status"] == "UP"

    for service in ("appointments", "laboratory"):
        response = client.post(
            f"/simulate/{service}/up",
            headers=HEADERS
        )
        assert response.status_code == 200

        response = client.get(f"/services/{service}")
        assert response.status_code == 200


@pytest.mark.parametrize("service", [
    "appointments",
    "pharmacy",
    "laboratory"
])
def test_unauthorized_simulation_rejected(client, service):
    response = client.post(
        f"/simulate/{service}/down",
        headers={"X-Simulation-Token": "wrong-token"}
    )

    assert response.status_code == 403

    response = client.get(f"/services/{service}")
    assert response.status_code == 200
