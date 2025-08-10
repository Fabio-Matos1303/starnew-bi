from fastapi.testclient import TestClient
import sys, os
sys.path.append(os.path.dirname(__file__))
from app.main import app
from app.api.v1.routes import vendas as vendas_routes
from utils_fake_db import FakeEngine, _FakeMapResult, _FakeScalar


class FakeEngineVendas(FakeEngine):
    def connect(self):
        class Conn:
            def __enter__(self): return self
            def __exit__(self, et, ev, tb): return False
            def execute(self, sql, params=None):
                s = str(sql).lower()
                if 'from vendas' in s and 'sum(total)' in s and 'group by' not in s:
                    return _FakeScalar(100.0)
                if 'from vendas' in s and 'count(*)' in s:
                    return _FakeScalar(5)
                if 'from vendas' in s and 'group by' in s:
                    return _FakeMapResult([
                        {'dia': '2025-08-01', 'total': 20.0},
                        {'dia': '2025-08-02', 'total': 80.0},
                    ])
                if 'from itens_venda' in s:
                    return _FakeMapResult([
                        {'d': 'Produto A', 'ocorrencias': 3, 'quantidade_total': 5, 'total_receita': 50.0},
                        {'d': 'Produto B', 'ocorrencias': 2, 'quantidade_total': 3, 'total_receita': 30.0},
                    ])
                return _FakeMapResult([])
        return Conn()


def setup_module():
    vendas_routes.get_sync_engine = lambda: FakeEngineVendas()


def test_faturamento_ok():
    c = TestClient(app)
    r = c.get('/api/v1/vendas/faturamento')
    assert r.status_code == 200
    p = r.json()
    assert p['total'] == 100.0
    assert len(p['por_dia']) == 2


def test_ticket_medio_ok():
    c = TestClient(app)
    r = c.get('/api/v1/vendas/ticket-medio')
    assert r.status_code == 200
    p = r.json()
    assert p['ticket_medio'] == 20.0
    assert p['vendas'] == 5


def test_top_produtos_ok():
    c = TestClient(app)
    r = c.get('/api/v1/vendas/top-produtos')
    assert r.status_code == 200
    arr = r.json()
    assert len(arr) == 2
    assert arr[0]['descricao'] == 'Produto A'
