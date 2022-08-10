import imp
from pydoc import Doc
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session
from cardioBackend import schemas
from cardioBackend.oauth2 import get_current_user
from cardioBackend.schemas import PyObjectId
from cardioBackend.database import db
from cardioBackend.hashing import Hash
from bson import ObjectId
from typing import List
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/user", tags=["user"])
collection = db.users

@router.get("/", status_code=200)
async def get_users(current_user: schemas.User = Depends(get_current_user)):
    arr = await collection.find().to_list(1000)
    users = []
    for user in arr:
        users.append(schemas.User(**user))
    return users

@router.get("/me", status_code=200)
async def get_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@router.get("/{id}", status_code=200)
async def get_user_by_id(id, current_user: schemas.User = Depends(get_current_user)):
    data = await collection.find_one({'_id': id})
    if data is None:
        raise HTTPException(status_code=404, detail='Oops! User not found.')
    return schemas.User(**data)

@router.put("/{id}", status_code=200)
async def edit_user_details(id, user: schemas.UpdateUser, current_user: schemas.User = Depends(get_current_user)):
    user = {k: v for k, v in user.dict().items() if v is not None}

    if len(user) >= 1:
        update_result = await collection.update_one({"_id": id}, {"$set": user})

        if update_result.modified_count == 1:
            if (
                updated_user := collection.find_one({"_id": id})
            ) is not None:
                return updated_user

    if (existing_user := await collection.find_one({"_id": id})) is not None:
        return existing_user

    raise HTTPException(status_code=404, detail=f"User {id} not found")

@router.delete("/{id}", status_code=203)
async def delete_user(id, current_user: schemas.User = Depends(get_current_user)):
    delete_result = await collection.delete_one({"_id":id})
    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=[])

    raise HTTPException(status_code=404, detail=f"User {id} not found")