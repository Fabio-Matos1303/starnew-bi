import json
from fastapi.testclient import TestClient
from app.main import app


def test_health_ok():
    client = TestClient(app)
    r = client.get('/api/v1/health')
    assert r.status_code == 200
    payload = r.json()
    assert 'status' in payload and payload['status'] == 'ok'
    assert 'db' in payload
