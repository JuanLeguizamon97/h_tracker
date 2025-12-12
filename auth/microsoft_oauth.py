from authlib.integrations.starlette_client import OAuth
from config.settings import settings

oauth = OAuth()

oauth.register(
    name="microsoft",
    client_id=settings.MICROSOFT_CLIENT_ID,
    client_secret=settings.MICROSOFT_CLIENT_SECRET,
    server_metadata_url=(
        f"https://login.microsoftonline.com/"
        f"{settings.MICROSOFT_TENANT_ID}/v2.0/.well-known/openid-configuration"
    ),
    client_kwargs={"scope": "openid profile email"},
)