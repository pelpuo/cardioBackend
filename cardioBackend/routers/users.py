import imp
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session
from cardioBackend import schemas
from cardioBackend.schemas import Roles
from cardioBackend.oauth2 import get_current_user
from cardioBackend.database import db

router = APIRouter(prefix="/user", tags=["user"])
collection = db.users

@router.get("/", status_code=200)
async def get_users(current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != Roles.ADMIN and current_user.role != Roles.TECHNICIAN:
        raise HTTPException(status_code=403, detail='Forbidden! Url is not permitted to this user.')
    arr = await collection.find().to_list(1000)
    users = []
    for user in arr:
        users.append(schemas.User(**user))
    return users

@router.get("/me", status_code=200)
async def get_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@router.get("/info", status_code=200)
async def get_user_info(current_user: schemas.User = Depends(get_current_user)):
    data = await collection.find_one({'_id': current_user.id})
    if data is None:
        raise HTTPException(status_code=404, detail='Oops! User not found.')
    return schemas.User(**data)

@router.get("/{id}", status_code=200)
async def get_user_by_id(id, current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != Roles.ADMIN or current_user.id != id:
        raise HTTPException(status_code=403, detail='Forbidden! Url is not permitted to this user.')
    data = await collection.find_one({'_id': id})
    if data is None:
        raise HTTPException(status_code=404, detail='Oops! User not found.')
    return schemas.User(**data)

@router.put("/{id}", status_code=200)
async def edit_user_details(id, user: schemas.UpdateUser, current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != Roles.ADMIN or current_user.id != id:
        raise HTTPException(status_code=403, detail='Forbidden! Url is not permitted to this user.')
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
    if current_user.role != Roles.ADMIN or current_user.id != id:
        raise HTTPException(status_code=403, detail='Forbidden! Url is not permitted to this user.')
    delete_result = await collection.delete_one({"_id":id})
    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=[])

    raise HTTPException(status_code=404, detail=f"User {id} not found")