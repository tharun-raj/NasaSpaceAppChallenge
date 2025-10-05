from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel
from typing import Optional, List
from db import insert_post, insert_comment, get_posts_with_comments

router = APIRouter()

# Input format
class PostInput(BaseModel):
    user_id: int
    title: str
    topic: str
    content: str
    coordinates: List[float]

class CommentInput(BaseModel):
    post_id: int
    user_id: int
    comment: str

# create post function
@router.post("/create-post")
def create_post(data: PostInput):
    try:
        insert_post(data.user_id, data.title, data.topic, data.content, data.coordinates)
        return {"message": "Post created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#add comment function
@router.post("/add-comment")
def add_comment(data: CommentInput):
    try:
        insert_comment(data.post_id, data.user_id, data.comment)
        return {"message": "Comment added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#get forum data function
@router.get("/get-forum-thread")
def get_thread(post_id: int = Query(None, description="Post ID"),):
    try:
        thread = get_posts_with_comments(post_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found.")
        return thread
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))