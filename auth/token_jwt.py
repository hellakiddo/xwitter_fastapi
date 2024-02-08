from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException

SECRET_KEY = "xwitter_fastapi"
ALGORITHM = "HS256"

def create_jwt_token(payload: dict, expires_delta: timedelta) -> str:
    expires_at = datetime.utcnow() + expires_delta
    token_payload = {"exp": expires_at, **payload}
    jwt_token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

    return jwt_token
