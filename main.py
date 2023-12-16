import databases
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from db.db_init import Post
from endpoints.posts import create_post, get_all_posts, get_post_by_id, update_post, delete_post, router

# Instantiate FastAPI
app = FastAPI()

app.include_router(router, prefix="/api")

from db.db_init import get_db
from main import app
from security.secure_config import verify_user, create_access_token


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: databases.Database = Depends(get_db)):
    user = verify_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_data = {"sub": user["id"], "username": user["username"]}
    access_token = create_access_token(access_token_data)
    return {"access_token": access_token, "token_type": "bearer"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
