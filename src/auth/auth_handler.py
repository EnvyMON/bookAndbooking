from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from fastapi import HTTPException, status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "7fa6b4307b1ec9378d826ff6a0b81acb0c24978423b204cfb3fbbd987525a32b5e42d397bf0659560f4c2c44b634c4d3cd6bf36d47c6457441d4c629d2a36575"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode_data = data.copy()
    
    if expires_delta:
        expires = datetime.utcnow() + expires_delta
    else:
        expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode_data.update(
        {
            "exp": expires
        }
    )
    
    encoded_jwt = jwt.encode(to_encode_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
    
def is_token_valid(token: str):
    
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
        expire = payload.get("exp")
        if expire:
            if expire < datetime.timestamp(datetime.utcnow()):
                return False
            else:
                return True
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not find expire. ",
                headers={"WWW-Authenticate": "Bearer"}
            )    
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find expire. ",
            headers={"WWW-Authenticate": "Bearer"}
        ) 

def extract_email_from_token(token: str):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM)
        email = payload.get("email")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not find expire. ",
                headers={"WWW-Authenticate": "Bearer"}
            )  
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find expire. ",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return email