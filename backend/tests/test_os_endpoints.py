from fastapi.testclient import TestClient
import sys, os
sys.path.append(os.path.dirname(__file__))
from app.main import app
from app.api.v1.routes import os as os_routes
from utils_fake_db import FakeEngine


def setup_module():
    # Monkeypatch engine getter to avoid real DB on tests
    os_routes.get_sync_engine = lambda: FakeEngine()


def test_os_status_empty_ok():
    c = TestClient(app)
    r = c.get('/api/v1/os/status')
    assert r.status_code == 200
    payload = r.json()
    assert 'total' in payload and isinstance(payload['total'], int)
    assert 'distribuicao' in payload and isinstance(payload['distribuicao'], dict)


def test_os_volume_empty_ok():
    c = TestClient(app)
    r = c.get('/api/v1/os/volume')
    assert r.status_code == 200
    payload = r.json()
    assert 'total' in payload and isinstance(payload['total'], int)
    assert isinstance(payload['por_dia'], list)


def test_os_tmc_empty_ok():
    c = TestClient(app)
    r = c.get('/api/v1/os/tempo-medio-conclusao')
    assert r.status_code == 200
    payload = r.json()
    assert payload['amostras'] == 0


def test_os_list_empty_ok():
    c = TestClient(app)
    r = c.get('/api/v1/os/list')
    assert r.status_code == 200
    payload = r.json()
    assert 'total' in payload and isinstance(payload['total'], int)
    assert payload['items'] == []
