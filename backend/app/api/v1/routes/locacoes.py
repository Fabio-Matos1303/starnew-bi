from typing import Dict, List, Optional
from datetime import datetime, date

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from ....core.database import get_sync_engine

router = APIRouter(prefix="/locacoes")


def _parse_period(from_: Optional[str], to_: Optional[str]) -> Dict[str, Optional[str]]:
    try:
        if from_:
            datetime.strptime(from_, "%Y-%m-%d")
        if to_:
            datetime.strptime(to_, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Parâmetro de data inválido. Use YYYY-MM-DD")
    return {"from": from_, "to": to_}


class SerieDia(BaseModel):
    dia: date
    total: float


class FaturamentoResponse(BaseModel):
    total: float
    por_dia: List[SerieDia]


@router.get("/faturamento", response_model=FaturamentoResponse)
def faturamento(
    from_: Optional[str] = Query(None, alias="from"),
    to_: Optional[str] = Query(None, alias="to"),
):
    periodo = _parse_period(from_, to_)
    where = []
    params: Dict[str, str] = {}
    if periodo["from"]:
        where.append("created_at >= :from")
        params["from"] = f"{periodo['from']} 00:00:00"
    if periodo["to"]:
        where.append("created_at <= :to")
        params["to"] = f"{periodo['to']} 23:59:59"
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    engine = get_sync_engine()
    with engine.connect() as conn:
        total = conn.execute(text(f"SELECT COALESCE(SUM(total),0) FROM locacoes {where_sql}"), params).scalar_one()
        rows = conn.execute(
            text(
                f"SELECT DATE(created_at) AS dia, COALESCE(SUM(total),0) AS total "
                f"FROM locacoes {where_sql} GROUP BY DATE(created_at) ORDER BY dia ASC"
            ),
            params,
        ).mappings().all()

    return FaturamentoResponse(
        total=float(total or 0), por_dia=[SerieDia(dia=r["dia"], total=float(r["total"])) for r in rows]
    )


class TopItem(BaseModel):
    descricao: str
    ocorrencias: int
    quantidade_total: float
    total_receita: float


@router.get("/top-itens", response_model=List[TopItem])
def top_itens(
    from_: Optional[str] = Query(None, alias="from"),
    to_: Optional[str] = Query(None, alias="to"),
    limit: int = Query(5, ge=1, le=50),
):
    periodo = _parse_period(from_, to_)
    filters = []
    params: Dict[str, object] = {"limit": limit}
    if periodo["from"]:
        filters.append("l.created_at >= :from")
        params["from"] = f"{periodo['from']} 00:00:00"
    if periodo["to"]:
        filters.append("l.created_at <= :to")
        params["to"] = f"{periodo['to']} 23:59:59"
    where_sql = ("WHERE " + " AND ".join(filters)) if filters else ""

    sql = (
        "SELECT il.descricao AS d, COUNT(*) AS ocorrencias, "
        "COALESCE(SUM(il.quantidade),0) AS quantidade_total, COALESCE(SUM(il.total),0) AS total_receita "
        "FROM itens_locacao il JOIN locacoes l ON l.id = il.locacao_id "
        f"{where_sql} "
        "GROUP BY il.descricao ORDER BY total_receita DESC, ocorrencias DESC LIMIT :limit"
    )

    engine = get_sync_engine()
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()

    return [
        TopItem(
            descricao=r["d"] or "",
            ocorrencias=int(r["ocorrencias"] or 0),
            quantidade_total=float(r["quantidade_total"] or 0),
            total_receita=float(r["total_receita"] or 0),
        )
        for r in rows
    ]


class OcupacaoResponse(BaseModel):
    ativos: int
    ocupados: int
    taxa: Optional[float]


@router.get("/taxa-ocupacao", response_model=OcupacaoResponse)
def taxa_ocupacao():
    """Calcula taxa de ocupação com base em produtos: ocupados/ativos.

    Ativos: produtos com is_ativo=1
    Ocupados: status IN ('locado','em_posse_cliente')
    """
    engine = get_sync_engine()
    with engine.connect() as conn:
        ativos = conn.execute(text("SELECT COUNT(*) FROM produtos WHERE is_ativo = 1")).scalar_one()
        ocupados = conn.execute(
            text("SELECT COUNT(*) FROM produtos WHERE is_ativo = 1 AND status IN ('locado','em_posse_cliente')")
        ).scalar_one()
    ativos = int(ativos or 0)
    ocupados = int(ocupados or 0)
    taxa = (ocupados / ativos) if ativos > 0 else None
    return OcupacaoResponse(ativos=ativos, ocupados=ocupados, taxa=taxa)
