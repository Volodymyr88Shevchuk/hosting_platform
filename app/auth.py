from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Simpele "fake" users database
fake_users_db = {
    "alice": {
        "username": "alice",
        "hashed_password": "$2b$12$NgfWKw7/xzrrZTzuLmSnMuGh/B3XXjwZi.VT7gEwmTO9xQKC7M9Me"
,  # wachtwoord: alice123
    },
    "bob": {
        "username": "bob",
        "hashed_password": "$2a$12$Uh1QdIWgcznXP9D6Qfps4uzoSXOk9kKBQd.iIwsFWB5TbHNw9MrMm",  # wachtwoord: bob123
    },
}

SECRET_KEY = "supergeheim"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    return db.get(username)

def authenticate_user(username: str, password: str):
    user = get_user(fake_users_db, username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)
    user = get_user(fake_users_db, username)
    if user is None:
        raise HTTPException(status_code=401)
    return user

