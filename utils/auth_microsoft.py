from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer

azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id="6cda0fcc-09b3-4173-b6cc-07df8bf2b82b",  # <- debe igualar `aud`
    tenant_id="9a347a67-e3c3-4de7-9c88-449af6f6c092",
    scopes={"api://6cda0fcc-09b3-4173-b6cc-07df8bf2b82b/user_impersonation": "user_impersonation"},
    allow_guest_users=True
)