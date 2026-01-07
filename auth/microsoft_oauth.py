from authlib.integrations.starlette_client import OAuth
from core.settings import settings

oauth = OAuth()

oauth.register(     
    name="microsoft",     
    client_id=settings.MICROSOFT_CLIENT_ID,   
    client_secret=settings.MICROSOFT_CLIENT_SECRET,  
    server_metadata_url="https://login.microsoftonline.com/c490fdea-5603-456c-b252-b0e9065f6c39/v2.0/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email"}
    )
 

 