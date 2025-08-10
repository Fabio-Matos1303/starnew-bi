from fastapi.testclient import TestClient
import sys, os
sys.path.append(os.path.dirname(__file__))
from app.main import app
from app.api.v1.routes import vendas as vendas_routes
from utils_fake_db import FakeEngine, _FakeMapResult


class FakeEngineExport(FakeEngine):
    def connect(self):
        class Conn:
            def __enter__(self): return self
            def __exit__(self, et, ev, tb): return False
            def execute(self, sql, params=None):
                s = str(sql).lower()
                if 'from itens_venda' in s and 'join vendas' in s:
                    return _FakeMapResult([
                        {'descricao': 'Produto, X', 'quantidade': 2, 'total': 10.5, 'data': '2025-08-01 10:00:00'},
                        {'descricao': 'Produto Y', 'quantidade': 1, 'total': 5.0, 'data': '2025-08-01 11:00:00'},
                    ])
                return _FakeMapResult([])
        return Conn()


def setup_module():
    vendas_routes.get_sync_engine = lambda: FakeEngineExport()


def test_export_csv_content():
    c = TestClient(app)
    r = c.get('/api/v1/vendas/export')
    assert r.status_code == 200
    assert r.headers.get('Content-Type','').startswith('text/csv')
    body = r.text.strip().splitlines()
    assert body[0] == 'descricao,quantidade,total,data'
    assert body[1].startswith('Produto  X,2,10.5,')  # vírgula do nome removida
