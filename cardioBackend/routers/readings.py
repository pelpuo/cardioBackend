from pydoc import Doc
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session
from cardioBackend import schemas
from cardioBackend.oauth2 import get_current_user
from cardioBackend.schemas import PyObjectId, Roles
from cardioBackend.database import db
from bson import ObjectId
from typing import List
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/reading", tags=["reading"])
collection = db.readings

@router.get("/", status_code=200)
async def get_readings(current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != Roles.TECHNICIAN or current_user.is_verified == False:
        raise HTTPException(status_code=403, detail='Forbidden! Url is not permitted to this user.')
    arr = await collection.find().to_list(1000)
    readings = []
    for reading in arr:
        readings.append(schemas.ShowReading(**reading))
    return readings

@router.get("/patient/{id}", status_code=200)
async def get_readings_by_patient_id(id, current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != Roles.TECHNICIAN or current_user.role != Roles.DOCTOR or current_user.is_verified == False:
        raise HTTPException(status_code=403, detail='Forbidden! Url is not permitted to this user.')
    arr = await collection.find({'patient_id': id}).to_list(1000)
    readings = []
    for reading in arr:
        readings.append(schemas.ShowReading(**reading))
    return readings

@router.get("/{id}", status_code=200)
async def get_reading_by_id(id, current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != Roles.TECHNICIAN or current_user.role != Roles.DOCTOR or current_user.is_verified == False:
        raise HTTPException(status_code=403, detail='Forbidden! Url is not permitted to this user.')
    data = await collection.find_one({'_id': id})
    ecg_values = await db.ecgValues.find_one({'reading_id': id})
    if data is None:
        raise HTTPException(status_code=404, detail='Reading not found.')
    return schemas.Reading(**data, values=ecg_values["values"])

@router.post("/", status_code=201)
async def add_reading(request: schemas.Reading, current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != Roles.TECHNICIAN or current_user.role != Roles.DOCTOR or current_user.is_verified == False:
        raise HTTPException(status_code=403, detail='Forbidden! Url is not permitted to this user.')
    new_reading = schemas.ShowReading(
        patient_id =request.patient_id, 
        hospital_name =request.hospital_name, 
        lead_type =request.lead_type, 
        lead_placement = request.lead_placement, 
        speed = request.speed,
        limb = request.limb,
        chest = request.chest
        )

    new_reading = jsonable_encoder(new_reading)

    inserted_reading = await collection.insert_one(new_reading)
    reading_id = inserted_reading.inserted_id

    reading_vals = schemas.EgcValues(reading_id = reading_id, values = request.values)
    reading_vals = jsonable_encoder(reading_vals)
    await db.ecgValues.insert_one(reading_vals)
    
    return new_reading

@router.put("/{id}", status_code=200)
async def edit_reading_details(id, reading: schemas.ShowReading, current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != Roles.TECHNICIAN or current_user.is_verified == False:
        raise HTTPException(status_code=403, detail='Forbidden! Url is not permitted to this user.')
    reading = {k: v for k, v in reading.dict().items() if v is not None}

    if len(reading) >= 1:
        update_result = await collection.update_one({"_id": id}, {"$set": reading})

        if update_result.modified_count == 1:
            if (
                updated_reading := collection.find_one({"_id": id})
            ) is not None:
                return updated_reading

    if (existing_reading := await collection.find_one({"_id": id})) is not None:
        return existing_reading

    raise HTTPException(status_code=404, detail=f"Reading {id} not found")

@router.delete("/{id}", status_code=203)
async def delete_reading(id, current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != Roles.TECHNICIAN or current_user.is_verified == False:
        raise HTTPException(status_code=403, detail='Forbidden! Url is not permitted to this user.')
    delete_result = await collection.delete_one({"_id":id})
    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=[])

    raise HTTPException(status_code=404, detail=f"Reading {id} not found")