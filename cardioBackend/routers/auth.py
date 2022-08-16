import imp
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from cardioBackend import schemas, authToken
from cardioBackend.hashing import Hash
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from cardioBackend.database import db


router = APIRouter(tags=['Authentication'])

@router.post('/login')
async def login(request:OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({'email_address': request.username})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invalid Credentials")
    if not Hash.verify(user["password"], request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Incorrect password")

    access_token = authToken.create_access_token(data={
        "id": user["_id"], 
        "sub": user["email_address"], 
        "role": user["role"], 
        "is_verified": user["is_verified"]
        })
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=201)
async def register_user(request: schemas.User):
    new_user = schemas.User(
    first_name=request.first_name, 
    last_name= request.last_name, 
    email_address= request.email_address,
    password= Hash.bcrypt(request.password))

    new_user = jsonable_encoder(new_user)

    await db.users.insert_one(new_user)
    return new_user