from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from .core.database import get_sync_engine
import os

app = FastAPI(title="Starnew BI API", version="0.1.0")

@app.get("/api/v1/health")
def health():
    # API health with soft DB check (no hard failure)
    payload = {"status": "ok", "db": {"status": "ok"}}
    try:
        engine = get_sync_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        payload["db"] = {"status": "error", "detail": str(exc)}
    return payload
