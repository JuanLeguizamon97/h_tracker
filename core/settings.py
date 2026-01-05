
from pathlib import Path
from pydantic import AnyHttpUrl, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Forzar core/.env
CORE_DIR = Path(__file__).resolve().parent
ENV_FILE = CORE_DIR / ".env"

if not ENV_FILE.exists():
    raise FileNotFoundError(
        f"No se encontró el archivo .env requerido en: {ENV_FILE}\n"
        f"Créalo en esa ruta (core/.env) o ajusta la ruta forzada en core/settings.py."
    )

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Azure Entra ID (obligatorias)
    TENANT_ID: str
    APP_CLIENT_ID: str
    OPENAPI_CLIENT_ID: str | None = None

    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    SCOPE_DESCRIPTION: str = "user_impersonation"

    @computed_field
    def SCOPE_NAME(self) -> str:
        return f"api://{self.APP_CLIENT_ID}/{self.SCOPE_DESCRIPTION}"

    @computed_field
    def SCOPES(self) -> dict[str, str]:
        return {self.SCOPE_NAME: self.SCOPE_DESCRIPTION}

    # Alias útil para Swagger / azure.py
    @computed_field
    def AZURE_API_SCOPE(self) -> str:
        return self.SCOPE_NAME

settings = Settings()
