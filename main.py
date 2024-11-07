from typing import Union
from pymongo import MongoClient

from fastapi import FastAPI, Path, Query, Body
from pydantic import BaseModel, Field
from datetime import datetime

app = FastAPI()


client = MongoClient(
    "mongodb+srv://jorgeav527:jorgimetro527@cluster0.mn8kdim.mongodb.net/"
)
db = client["fastapi"]
collection = db["post"]


class Post(BaseModel):
    id: str
    title: str
    content: str
    created: datetime


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/api/v1/post")
def read_all_post():
    posts = collection.find()
    return [
        Post(
            id=str(post["_id"]),
            title=post["title"],
            content=post["content"],
            created=post["created"],
        )
        for post in posts
    ]
