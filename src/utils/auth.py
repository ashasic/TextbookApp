import os
from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT


class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv("AUTH_SECRET_KEY", "defaultsecret")


@AuthJWT.load_config
def get_config():
    return Settings()
