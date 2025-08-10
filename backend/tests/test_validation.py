from fastapi.testclient import TestClient
import sys, os
sys.path.append(os.path.dirname(__file__))
from app.main import app
from app.api.v1.routes import os as os_routes
from utils_fake_db import FakeEngine


def setup_module():
    os_routes.get_sync_engine = lambda: FakeEngine()


def test_invalid_date_returns_400():
    c = TestClient(app)
    r = c.get('/api/v1/os/volume?from=2025-99-01')
    assert r.status_code == 400
    assert 'data inválido' in r.text.lower()
