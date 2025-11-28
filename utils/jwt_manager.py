import jwt

def create_token(data: dict) -> str:
    token: str = jwt.encode(payload= data, key= "my_secret_key", algorithm = "HS256")
    return token

def validate_token(token:str) -> dict:
    data: dict = jwt.decode(token, key = "my_secret_key", algorithms = ['HS256'])
    return data