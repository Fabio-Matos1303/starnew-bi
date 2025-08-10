from fastapi.testclient import TestClient
import sys, os
sys.path.append(os.path.dirname(__file__))
from app.main import app
from app.api.v1.routes import locacoes as loc_routes
from utils_fake_db import FakeEngine, _FakeMapResult, _FakeScalar


class FakeEngineLoc(FakeEngine):
    def connect(self):
        class Conn:
            def __enter__(self): return self
            def __exit__(self, et, ev, tb): return False
            def execute(self, sql, params=None):
                s = str(sql).lower()
                if 'from locacoes' in s and 'sum(total)' in s and 'group by' not in s:
                    return _FakeScalar(123.45)
                if 'from locacoes' in s and 'group by' in s:
                    return _FakeMapResult([
                        {'dia': '2025-08-01', 'total': 23.45},
                        {'dia': '2025-08-02', 'total': 100.0},
                    ])
                if 'from itens_locacao' in s:
                    return _FakeMapResult([
                        {'d': 'Item X', 'ocorrencias': 2, 'quantidade_total': 2, 'total_receita': 70.0},
                        {'d': 'Item Y', 'ocorrencias': 1, 'quantidade_total': 1, 'total_receita': 50.0},
                    ])
                if 'from produtos' in s and 'status in' in s:
                    return _FakeScalar(5)
                if 'from produtos' in s and 'is_ativo = 1' in s and 'status in' not in s:
                    return _FakeScalar(10)
                return _FakeMapResult([])
        return Conn()


def setup_module():
    loc_routes.get_sync_engine = lambda: FakeEngineLoc()


def test_loc_faturamento_ok():
    c = TestClient(app)
    r = c.get('/api/v1/locacoes/faturamento')
    assert r.status_code == 200
    p = r.json()
    assert p['total'] == 123.45
    assert len(p['por_dia']) == 2


def test_loc_top_itens_ok():
    c = TestClient(app)
    r = c.get('/api/v1/locacoes/top-itens')
    assert r.status_code == 200
    arr = r.json()
    assert len(arr) == 2
    assert arr[0]['descricao'] == 'Item X'


def test_loc_taxa_ocupacao_ok():
    c = TestClient(app)
    r = c.get('/api/v1/locacoes/taxa-ocupacao')
    assert r.status_code == 200
    p = r.json()
    assert p['ativos'] == 10 and p['ocupados'] == 5
    assert abs(p['taxa'] - 0.5) < 1e-6
