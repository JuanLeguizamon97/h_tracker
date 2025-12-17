from pydantic import AnyHttpUrl, computed_field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TENANT_ID: str
    APP_CLIENT_ID: str
    OPENAPI_CLIENT_ID: str | None = None

    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = [
        "http://localhost:3000",  # tu portal
        "http://localhost:8000",  # docs
    ]

    SCOPE_DESCRIPTION: str = "user_impersonation"

    @computed_field
    @property
    def SCOPE_NAME(self) -> str:
        # scope “full name” estilo api://<app_client_id>/user_impersonation
        return f"api://{self.APP_CLIENT_ID}/{self.SCOPE_DESCRIPTION}"

    @computed_field
    @property
    def SCOPES(self) -> dict[str, str]:
        # mapping: { scope_full_name: description }
        return {self.SCOPE_NAME: self.SCOPE_DESCRIPTION}

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()
