import os
from dotenv import load_dotenv
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer

load_dotenv()

AZURE_APP_CLIENT_ID = os.getenv("AZURE_APP_CLIENT_ID", "6cda0fcc-09b3-4173-b6cc-07df8bf2b82b")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "9a347a67-e3c3-4de7-9c88-449af6f6c092")
AZURE_API_SCOPE = os.getenv(
    "AZURE_API_SCOPE",
    f"api://{AZURE_APP_CLIENT_ID}/user_impersonation",
)

azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=AZURE_APP_CLIENT_ID,
    tenant_id=AZURE_TENANT_ID,
    scopes={AZURE_API_SCOPE: "user_impersonation"},
    allow_guest_users=True,
)
