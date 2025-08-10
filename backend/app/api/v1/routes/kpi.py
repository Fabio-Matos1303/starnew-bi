from typing import Dict, Optional
from fastapi import APIRouter, Query
from sqlalchemy import text

from ....core.database import get_sync_engine

router = APIRouter(prefix="/kpi")


def _period_clause(column: str, from_: Optional[str], to_: Optional[str], params: Dict[str, str]) -> str:
    clauses = []
    if from_:
        clauses.append(f"{column} >= :from")
        params["from"] = f"{from_} 00:00:00"
    if to_:
        clauses.append(f"{column} <= :to")
        params["to"] = f"{to_} 23:59:59"
    return ("WHERE " + " AND ".join(clauses)) if clauses else ""


@router.get("/geral")
def kpi_geral(
    from_: Optional[str] = Query(None, alias="from"),
    to_: Optional[str] = Query(None, alias="to"),
):
    """KPIs gerais do período: receita total (vendas+OS+locações), participação, novos clientes e status de OS."""
    # Totais por área (cada consulta recebe seu próprio dict de params)
    params_v: Dict[str, str] = {}
    params_os: Dict[str, str] = {}
    params_l: Dict[str, str] = {}
    params_cli: Dict[str, str] = {}

    where_v = _period_clause("created_at", from_, to_, params_v)
    where_os = _period_clause("created_at", from_, to_, params_os)
    where_l = _period_clause("created_at", from_, to_, params_l)
    where_cli = _period_clause("created_at", from_, to_, params_cli)

    sql_vendas_total = f"SELECT COALESCE(SUM(total),0) AS t FROM vendas {where_v}"
    sql_os_total = f"SELECT COALESCE(SUM(valor_total),0) AS t FROM ordens_servico {where_os}"
    sql_loc_total = f"SELECT COALESCE(SUM(total),0) AS t FROM locacoes {where_l}"
    sql_novos_clientes = f"SELECT COUNT(*) AS c FROM clientes {where_cli}"

    # Status de OS
    params_os_status: Dict[str, str] = {}
    where_os_status = _period_clause("created_at", from_, to_, params_os_status)
    sql_os_status = (
        f"SELECT UPPER(status) AS s, COUNT(*) AS c FROM ordens_servico {where_os_status} "
        "GROUP BY UPPER(status)"
    )

    engine = get_sync_engine()
    with engine.connect() as conn:
        v = float(conn.execute(text(sql_vendas_total), params_v).scalar_one() or 0)
        o = float(conn.execute(text(sql_os_total), params_os).scalar_one() or 0)
        l = float(conn.execute(text(sql_loc_total), params_l).scalar_one() or 0)
        novos = int(conn.execute(text(sql_novos_clientes), params_cli).scalar_one() or 0)
        rows = conn.execute(text(sql_os_status), params_os_status).mappings().all()

    receita_total = v + o + l
    participacao = {"vendas": v, "os": o, "locacoes": l}
    os_status = {r["s"] or "": int(r["c"]) for r in rows}

    return {
        "receita_total": receita_total,
        "participacao": participacao,
        "novos_clientes": novos,
        "os_status": os_status,
    }
