from fastapi.testclient import TestClient
import sys, os
sys.path.append(os.path.dirname(__file__))
from app.main import app
from app.api.v1.routes import kpi as kpi_routes
from utils_fake_db import FakeEngine


def setup_module():
    kpi_routes.get_sync_engine = lambda: FakeEngine()


def test_kpi_geral_ok():
    c = TestClient(app)
    r = c.get('/api/v1/kpi/geral')
    assert r.status_code == 200
    payload = r.json()
    assert 'receita_total' in payload
    assert 'participacao' in payload
    assert 'novos_clientes' in payload
    assert 'os_status' in payload
