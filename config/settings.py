from pydantic import BaseSettings

class Settings(BaseSettings):
    MICROSOFT_CLIENT_ID: str
    MICROSOFT_CLIENT_SECRET: str
    MICROSOFT_TENANT_ID: str

    JWT_SECRET_KEY: str = "CAMBIA_ESTA_CLAVE_SUPER_SECRETA"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_HOURS: int = 8

    class Config:
        env_file = ".venv"

settings = Settings()
