import os
from typing import List


class Settings:
    """Application settings loaded from environment variables."""

    api_title: str = "Starnew BI API"
    api_version: str = "0.1.0"

    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_user: str = os.getenv("DB_USER", "root")
    db_password: str = os.getenv("DB_PASSWORD", "")
    db_name: str = os.getenv("DB_NAME", "starnew")

    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "*")

    @property
    def allowed_origins(self) -> List[str]:
        if self.frontend_origin == "*":
            return ["*"]
        return [origin.strip() for origin in self.frontend_origin.split(",") if origin.strip()]


settings = Settings()
