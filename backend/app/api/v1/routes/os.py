from datetime import date, datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel
from sqlalchemy import text

from ....core.database import get_sync_engine

router = APIRouter(prefix="/os")


class VolumeDia(BaseModel):
    dia: date
    total: int


class VolumeResponse(BaseModel):
    total: int
    por_dia: List[VolumeDia]


class StatusResponse(BaseModel):
    total: int
    distribuicao: Dict[str, int]


class TmcResponse(BaseModel):
    dias: Optional[float]
    amostras: int


def _parse_periodo(from_: Optional[str], to_: Optional[str]) -> Dict[str, Optional[str]]:
    # Expect YYYY-MM-DD; return as strings (MySQL will parse)
    if from_:
        datetime.strptime(from_, "%Y-%m-%d")
    if to_:
        datetime.strptime(to_, "%Y-%m-%d")
    return {"from": from_, "to": to_}


@router.get("/volume", response_model=VolumeResponse)
def os_volume(
    from_: Optional[str] = Query(None, alias="from", description="YYYY-MM-DD"),
    to_: Optional[str] = Query(None, alias="to", description="YYYY-MM-DD"),
):
    periodo = _parse_periodo(from_, to_)
    where = []
    params = {}
    if periodo["from"]:
        where.append("created_at >= :from")
        params["from"] = f"{periodo['from']} 00:00:00"
    if periodo["to"]:
        where.append("created_at <= :to")
        params["to"] = f"{periodo['to']} 23:59:59"
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    engine = get_sync_engine()
    with engine.connect() as conn:
        total = conn.execute(text(f"SELECT COUNT(*) AS c FROM ordens_servico {where_sql}"), params).scalar_one()
        rows = conn.execute(
            text(
                f"SELECT DATE(created_at) AS dia, COUNT(*) AS total "
                f"FROM ordens_servico {where_sql} GROUP BY DATE(created_at) ORDER BY dia ASC"
            ),
            params,
        ).mappings().all()

    return VolumeResponse(total=int(total or 0), por_dia=[VolumeDia(dia=r["dia"], total=int(r["total"])) for r in rows])


@router.get("/status", response_model=StatusResponse)
def os_status(
    from_: Optional[str] = Query(None, alias="from", description="YYYY-MM-DD"),
    to_: Optional[str] = Query(None, alias="to", description="YYYY-MM-DD"),
):
    periodo = _parse_periodo(from_, to_)
    where = []
    params = {}
    if periodo["from"]:
        where.append("created_at >= :from")
        params["from"] = f"{periodo['from']} 00:00:00"
    if periodo["to"]:
        where.append("created_at <= :to")
        params["to"] = f"{periodo['to']} 23:59:59"
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    engine = get_sync_engine()
    with engine.connect() as conn:
        total = conn.execute(text(f"SELECT COUNT(*) FROM ordens_servico {where_sql}"), params).scalar_one()
        rows = conn.execute(
            text(
                f"SELECT UPPER(status) AS s, COUNT(*) AS total FROM ordens_servico {where_sql} GROUP BY UPPER(status) ORDER BY s"
            ),
            params,
        ).mappings().all()

    distrib: Dict[str, int] = {r["s"] or "": int(r["total"]) for r in rows}
    return StatusResponse(total=int(total or 0), distribuicao=distrib)


@router.get("/tempo-medio-conclusao", response_model=TmcResponse)
def os_tempo_medio_conclusao(
    from_: Optional[str] = Query(None, alias="from", description="YYYY-MM-DD (aplica em data_fim)"),
    to_: Optional[str] = Query(None, alias="to", description="YYYY-MM-DD (aplica em data_fim)"),
):
    periodo = _parse_periodo(from_, to_)
    where = ["data_inicio IS NOT NULL", "data_fim IS NOT NULL", "UPPER(status) = 'CONCLUIDA'"]
    params = {}
    if periodo["from"]:
        where.append("data_fim >= :from")
        params["from"] = periodo["from"]
    if periodo["to"]:
        where.append("data_fim <= :to")
        params["to"] = periodo["to"]
    where_sql = "WHERE " + " AND ".join(where)

    engine = get_sync_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text(
                f"SELECT AVG(TIMESTAMPDIFF(DAY, data_inicio, data_fim)) AS dias, COUNT(*) AS n "
                f"FROM ordens_servico {where_sql}"
            ),
            params,
        ).mappings().first()

    dias = float(row["dias"]) if row and row["dias"] is not None else None
    amostras = int(row["n"]) if row else 0
    return TmcResponse(dias=dias, amostras=amostras)
