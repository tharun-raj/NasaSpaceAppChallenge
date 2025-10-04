from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel
from typing import Optional, List
from .db import insert_coordinates,get_coordinates,delete_coordinates,update_coordinates

router = APIRouter()

# Input format
class LabelInput(BaseModel):
    user_id: int
    celestialObject: str
    title: str
    description: str
    coordinates: List[float]  # e.g. [102.09, -92.292]


@router.post("/add-labels/")
def add_coordinates(data: LabelInput):
    try:
        insert_coordinates(data.user_id,data.celestialObject,data.title,data.description, data.coordinates)
        return {"message": "Labels inserted successfully."}
    except Exception as e:
        print("❌ ERROR during add_coordinates:", e) 
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/get-labels/user_id/{user_id}")
def get_labels(
    user_id: int = Path(..., description="User ID"),
    celestial_object: Optional[str] = Query(None, description="Celestial object name"),
    title: Optional[str] = Query(None, description="Title of the label"),
    id: Optional[int] = Query(None, description="Label ID")
):
    try:
        print("🔍 GET /labels/get-labels triggered", flush=True)

        results = get_coordinates(user_id,id,title, celestial_object)
        if not results:
            raise HTTPException(status_code=404, detail="No matching labels found.")
        return {"labels": results}
    except Exception as e:
        print("❌ ERROR during get_coordinates:", e) 
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/delete-labels/id/{id}")
def delete_labels(
    id: Optional[int] = Path(...,description="label id",),
    user_id: Optional[int] = Query(None, description="User ID"),
    celestial_object: Optional[str] = Query(None, description="Celestial object name")
):
    try:
        result=delete_coordinates(id,user_id, celestial_object)
        if result:
            return {"message": "Label deleted successfully."}
    except Exception as e:
        print("❌ ERROR during delete_coordinates:", e) 
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/update-labels/id/{id}")
def update_labels(
    id: int = Path(..., description="Label ID"),
    # user_id: Optional[int] = Query(None, description="User ID"),
    # celestial_object: Optional[str] = Query(None, description="Celestial object name"),
    title: Optional[str] = Query(None, description="Title of the label"),
    description: Optional[str] = Query(None, description="Label description")
):
    try:
        result = update_coordinates(id, title, description)
        if result:
            return {"message": "Label updated successfully."}
        else:
            raise HTTPException(status_code=404, detail="Label not found or nothing to update.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

