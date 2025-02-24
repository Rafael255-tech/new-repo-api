from typing import Union, List, Optional, Any
from pymongo import MongoClient

from fastapi import FastAPI, Path, Query, Body, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

app = FastAPI()


def get_db():
    MONGODB_URI = "mongodb+srv://jorgeav527:jorgimetro527@cluster0.mn8kdim.mongodb.net/"
    try:
        client = MongoClient(MONGODB_URI)
        db = client["fastapi"]
        yield db
    finally:
        client.close()


class Post(BaseModel):
    id: str
    title: str
    content: str
    created: datetime


class PostCreate(BaseModel):
    title: str
    content: str


class PostUpdate(BaseModel):
    id: str
    title: str
    content: str


@app.get("/")
def read_root():
    return JSONResponse(content={"Hello": "World", "framework": "fastapi"})


@app.get("/api/v1/post", response_model=List[Post])
def read_all_post(db=Depends(get_db)) -> List[Post]:
    result = []
    posts = db["post"].find()
    for post in posts:
        result.append(
            Post(
                id=str(post["_id"]),
                title=post["title"],
                content=post["content"],
                created=post["created"],
            )
        )
    return result


@app.get("/api/v1/post/{post_id}", response_model=Post)
def read_one_post(post_id, db=Depends(get_db)) -> List[Post]:

    try:
        post = db["post"].find_one({"_id": ObjectId(post_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    if post is None:
        raise HTTPException(status_code=400, detail="Post not found")

    return Post(
        id=str(post["_id"]),
        title=post["title"],
        content=post["content"],
        created=post["created"],
    )


@app.post("/api/v1/post/create", response_model=Post)
def create_one_post(post: PostCreate, db=Depends(get_db)) -> Post:

    if not post.title:
        raise HTTPException(status_code=400, detail="title is required")

    created_time = datetime.now()

    new_post = {
        "title": post.title,
        "content": post.content,
        "created": created_time,
    }
    result = db["post"].insert_one(new_post)
    created_post = db["post"].find_one({"_id": result.inserted_id})

    return Post(
        id=str(created_post["_id"]),
        title=created_post["title"],
        content=created_post["content"],
        created=created_post["created"],
    )


@app.put("/api/v1/post/edit", response_model=Any)
def edit_one_post(post: PostUpdate, db=Depends(get_db)) -> Any:
    exiting_post = db["post"].find_one({"_id": ObjectId(post.id)})
    updated_post_data = {"title": post.title, "content": post.content}
    db["post"].update_one({"_id": ObjectId(post.id)}, {"$set": updated_post_data})
    updated_post = db["post"].find_one({"_id": ObjectId(post.id)})
    return (
        Post(
            id=str(exiting_post["_id"]),
            title=exiting_post["title"],
            content=exiting_post["content"],
            created=exiting_post["created"],
        ),
        Post(
            id=str(updated_post["_id"]),
            title=updated_post["title"],
            content=updated_post["content"],
            created=updated_post["created"],
        ),
    )


@app.delete("/api/v1/post/delete", response_model=Any)
def edit_one_post(post_id: str, db=Depends(get_db)) -> Any:
    try:
        post = db["post"].find_one({"_id": ObjectId(post_id)})
    except:
        raise HTTPException(status_code=400, detail="invalid Id")

    if post is None:
        raise HTTPException(status_code=400, detail="post not found")

    db["post"].delete_one({"_id": ObjectId(post_id)})
    return {"message": "Post borrado exitosamente"}
