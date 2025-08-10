from typing import Dict, List, Optional
from datetime import datetime, date

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import text

from ....core.database import get_sync_engine

router = APIRouter(prefix="/vendas")


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
        total = conn.execute(text(f"SELECT COALESCE(SUM(total),0) FROM vendas {where_sql}"), params).scalar_one()
        rows = conn.execute(
            text(
                f"SELECT DATE(created_at) AS dia, COALESCE(SUM(total),0) AS total "
                f"FROM vendas {where_sql} GROUP BY DATE(created_at) ORDER BY dia ASC"
            ),
            params,
        ).mappings().all()

    return FaturamentoResponse(
        total=float(total or 0), por_dia=[SerieDia(dia=r["dia"], total=float(r["total"])) for r in rows]
    )


class TicketMedioResponse(BaseModel):
    ticket_medio: Optional[float]
    vendas: int


@router.get("/ticket-medio", response_model=TicketMedioResponse)
def ticket_medio(
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
        soma = conn.execute(text(f"SELECT COALESCE(SUM(total),0) FROM vendas {where_sql}"), params).scalar_one()
        qtd = conn.execute(text(f"SELECT COUNT(*) FROM vendas {where_sql}"), params).scalar_one()

    qtd = int(qtd or 0)
    ticket = float(soma) / qtd if qtd > 0 else None
    return TicketMedioResponse(ticket_medio=ticket, vendas=qtd)


class TopProdutoItem(BaseModel):
    descricao: str
    ocorrencias: int
    quantidade_total: float
    total_receita: float


@router.get("/top-produtos", response_model=List[TopProdutoItem])
def top_produtos(
    from_: Optional[str] = Query(None, alias="from"),
    to_: Optional[str] = Query(None, alias="to"),
    limit: int = Query(5, ge=1, le=50),
):
    periodo = _parse_period(from_, to_)
    filters = []
    params: Dict[str, object] = {"limit": limit}
    if periodo["from"]:
        filters.append("v.created_at >= :from")
        params["from"] = f"{periodo['from']} 00:00:00"
    if periodo["to"]:
        filters.append("v.created_at <= :to")
        params["to"] = f"{periodo['to']} 23:59:59"
    where_sql = ("WHERE " + " AND ".join(filters)) if filters else ""

    sql = (
        "SELECT iv.descricao AS d, COUNT(*) AS ocorrencias, "
        "COALESCE(SUM(iv.quantidade),0) AS quantidade_total, COALESCE(SUM(iv.total),0) AS total_receita "
        "FROM itens_venda iv JOIN vendas v ON v.id = iv.venda_id "
        f"{where_sql} "
        "GROUP BY iv.descricao ORDER BY total_receita DESC, ocorrencias DESC LIMIT :limit"
    )

    engine = get_sync_engine()
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()

    return [
        TopProdutoItem(
            descricao=r["d"] or "",
            ocorrencias=int(r["ocorrencias"] or 0),
            quantidade_total=float(r["quantidade_total"] or 0),
            total_receita=float(r["total_receita"] or 0),
        )
        for r in rows
    ]


@router.get("/export", response_class=Response)
def export_csv(
    from_: Optional[str] = Query(None, alias="from"),
    to_: Optional[str] = Query(None, alias="to"),
):
    """Exporta itens de vendas no período em CSV (descricao, quantidade, total, data)."""
    periodo = _parse_period(from_, to_)
    filters = []
    params: Dict[str, object] = {}
    if periodo["from"]:
        filters.append("v.created_at >= :from")
        params["from"] = f"{periodo['from']} 00:00:00"
    if periodo["to"]:
        filters.append("v.created_at <= :to")
        params["to"] = f"{periodo['to']} 23:59:59"
    where_sql = ("WHERE " + " AND ".join(filters)) if filters else ""

    sql = (
        "SELECT iv.descricao, iv.quantidade, iv.total, v.created_at AS data "
        "FROM itens_venda iv JOIN vendas v ON v.id = iv.venda_id "
        f"{where_sql} ORDER BY v.created_at ASC, iv.id ASC"
    )

    engine = get_sync_engine()
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()

    # Monta CSV simples
    lines = ["descricao,quantidade,total,data"]
    for r in rows:
        desc = str(r["descricao"]).replace(",", " ")
        lines.append(f"{desc},{r['quantidade']},{r['total']},{r['data']}")
    csv_data = "\n".join(lines)
    headers = {"Content-Type": "text/csv; charset=utf-8", "Content-Disposition": "attachment; filename=vendas.csv"}
    return Response(content=csv_data, media_type="text/csv", headers=headers)
