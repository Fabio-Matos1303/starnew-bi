import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def _build_mysql_url() -> str:
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    db = os.getenv("DB_NAME", "starnew")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4"


def get_sync_engine() -> Engine:
    url = _build_mysql_url()
    engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
    )
    return engine
