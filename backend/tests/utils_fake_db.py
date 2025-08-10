class _FakeScalar:
    def __init__(self, value=0):
        self._value = value

    def scalar_one(self):
        return self._value


class _FakeMapResult:
    def __init__(self, rows=None):
        self._rows = rows or []

    def mappings(self):
        class _Self:
            def __init__(self, rows):
                self._rows = rows

            def all(self):
                return self._rows

            def first(self):
                return self._rows[0] if self._rows else None

        return _Self(self._rows)


class _FakeConn:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        sqls = str(sql).lower()
        # AVG TMC -> return {'dias': None, 'n': 0}
        if "avg(timestampdiff" in sqls:
            return _FakeMapResult([{ "dias": None, "n": 0 }])
        # GROUP BY status / volume / top-servicos -> empty
        if "group by" in sqls:
            return _FakeMapResult([])
        # SELECT ... FROM ordens_servico ... LIMIT ... -> list endpoint
        if "from ordens_servico" in sqls and "limit" in sqls:
            return _FakeMapResult([])
        # COUNT(*) or SUM(...) -> scalar 0
        if "count(" in sqls or "sum(" in sqls:
            return _FakeScalar(0)
        # Fallback maps empty
        return _FakeMapResult([])


class FakeEngine:
    def connect(self):
        return _FakeConn()
