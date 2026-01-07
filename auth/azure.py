from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
from core.settings import settings

azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=settings.AZURE_APP_CLIENT_ID,
    tenant_id=settings.AZURE_TENANT_ID,
    scopes={settings.AZURE_API_SCOPE: "access_api"},
)
