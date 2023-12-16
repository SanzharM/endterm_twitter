from datetime import datetime
from typing import List

import databases
from fastapi import Depends, HTTPException, APIRouter
from pydantic import BaseModel
from sqlalchemy import Table, select
from sqlalchemy.orm import Session

from db.db_init import User, get_db, metadata, engine, Post
from security.secure_config import verify_user

router = APIRouter()


# Pydantic models
class PostCreate(BaseModel):
    title: str
    text: str


class PostResponse(BaseModel):
    id: int
    title: str
    text: str
    created_at: datetime
    author_id: int


# Endpoints

@router.post("/posts/", response_model=PostResponse)
async def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(verify_user)):
    db_post = Post(**post.dict(), author_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@router.get("/posts/", response_model=List[PostResponse])
async def get_all_posts(db: Session = Depends(get_db)):
    query = select(Post)
    return db.execute(query).scalars().all()


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post_by_id(post_id: int, db: Session = Depends(get_db)):
    query = select(Post).filter(Post.id == post_id)
    post = db.execute(query).first()

    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@router.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(post_id: int, post: PostCreate, db: Session = Depends(get_db),
                      current_user: User = Depends(verify_user)):
    query = select(Post).filter(Post.id == post_id)
    db_post = db.execute(query).first()

    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if db_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")

    for key, value in post.dict().items():
        setattr(db_post, key, value)

    db.commit()
    db.refresh(db_post)
    return db_post


@router.delete("/posts/{post_id}", response_model=dict)
async def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(verify_user)):
    query = select(Post).filter(Post.id == post_id)
    db_post = db.execute(query).first()

    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if db_post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Permission denied")

    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}
