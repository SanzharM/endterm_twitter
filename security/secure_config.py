# OAuth2PasswordBearer for token authentication
from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from config.common import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password hashing
password_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Token functions
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Function to verify the username and password and return a user if successful
def verify_user(db, username: str, password: str):
    query = users.select().where(users.c.username == username)
    user = db.execute(query).fetchone()
    if user and password_hasher.verify(password, user["hashed_password"]):
        return user
