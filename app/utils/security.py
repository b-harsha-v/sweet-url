from datetime import datetime, timedelta, timezone

from jose import jwt
from jose import JWTError

SECRET_KEY = "super-secret-key"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_HOURS = 24


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = (
        datetime.now(timezone.utc)
        + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    )

    to_encode.update({
        "exp": expire
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def decode_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        return None