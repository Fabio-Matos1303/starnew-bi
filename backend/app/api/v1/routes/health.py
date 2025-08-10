from fastapi import APIRouter
from sqlalchemy import text

from ....core.database import get_sync_engine

router = APIRouter()


@router.get("/health")
def health():
    payload = {"status": "ok", "db": {"status": "ok"}}
    try:
        engine = get_sync_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        payload["db"] = {"status": "error", "detail": str(exc)}
    return payload
