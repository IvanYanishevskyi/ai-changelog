from fastapi.testclient import TestClient

from changelog.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "database" in data


def test_readiness():
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


def test_webhook_no_signature():
    resp = client.post(
        "/webhooks/github",
        json={"ref": "refs/heads/main", "repository": {"full_name": "test/repo"}, "commits": []},
        headers={"X-GitHub-Event": "push", "X-Hub-Signature-256": ""},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"
