import time
import uuid
import jwt
import os

SECRET_KEY = os.environ["JWT_SECRET"]
ISSUER = os.environ.get("IDM_ISSUER", "http://127.0.0.1:50051")
VALIDITY_SECONDS = 3600

blacklist = {}


def create_token(uid, role):
    payload = {
        "iss": ISSUER,
        "sub": uid,
        "exp": int(time.time()) + VALIDITY_SECONDS,
        "jti": str(uuid.uuid4()),
        "role": role,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def blacklist_token(token):
    blacklist[token] = True


def validate_token(token):
    if token in blacklist:
        return None
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        blacklist_token(token)
        return None