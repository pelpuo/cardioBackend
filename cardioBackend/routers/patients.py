from datetime import datetime
from json import JSONDecoder
import json
from pydoc import Doc
from types import SimpleNamespace
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

router = APIRouter(prefix="/patient", tags=["patient"])
collection = db.patients

@router.get("/", status_code=200)
async def get_patients(current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != Roles.ADMIN or current_user.role != Roles.TECHNICIAN or current_user.is_verified == False:
        raise HTTPException(status_code=403, detail='Forbidden! Url is not permitted to this user.')
    arr = await collection.find().to_list(1000)
    patients = []
    for patient in arr:
        patients.append(schemas.Patient(**patient))
    return patients

@router.get("/doctor/me", status_code=200)
async def get_patients_assigned_to_user(current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != Roles.DOCTOR or current_user.is_verified == False:
        raise HTTPException(status_code=403, detail='Forbidden! Url is not permitted to this user.')
    arr = await collection.find({'doctor_id': current_user.id}).to_list(1000)
    patients = []
    for patient in arr:
        patients.append(schemas.Patient(**patient))
    return patients

@router.get("/doctor/{id}", status_code=200)
async def get_patients_by_doctor_id(id, current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != Roles.ADMIN or current_user.role != Roles.TECHNICIAN or current_user.is_verified == False:
        raise HTTPException(status_code=403, detail='Forbidden! Url is not permitted to this user.')
    arr = await collection.find({'doctor_id': id}).to_list(1000)
    patients = []
    for patient in arr:
        patients.append(schemas.Patient(**patient))
    return patients

@router.get("/{id}", status_code=200)
async def get_patient_by_id(id, urrent_user: schemas.User = Depends(get_current_user)):
    data = await collection.find_one({'_id': id})
    if data is None:
        raise HTTPException(status_code=404, detail='Patient not found.')
    return schemas.Patient(**data)

@router.post("/", status_code=201)
async def add_patient(request: schemas.Patient, current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != Roles.TECHNICIAN or current_user.is_verified == False:
        raise HTTPException(status_code=403, detail='Forbidden! Url is not permitted to this user.')
    new_patient = schemas.Patient(first_name=request.first_name, 
    last_name= request.last_name, 
    email_address= request.email_address,
    gender= request.gender,
    date_of_birth= request.date_of_birth,
    doctor_id= request.doctor_id
    )

    new_patient = jsonable_encoder(new_patient)

    await collection.insert_one(new_patient)
    return new_patient

@router.put("/{id}", status_code=200)
async def edit_patient_details(id, patient: schemas.UpdatePatient, current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != Roles.TECHNICIAN or current_user.is_verified == False:
        raise HTTPException(status_code=403, detail='Forbidden! Url is not permitted to this user.')
    
    patient = {k: v for k, v in patient.dict().items() if v is not None}

    if len(patient) >= 1:
        update_result = await collection.update_one({"_id": id}, {"$set": patient})

        if update_result.modified_count == 1:
            if (
                updated_patient := collection.find_one({"_id": id})
            ) is not None:
                return updated_patient

    if (existing_patient := await collection.find_one({"_id": id})) is not None:
        return existing_patient

    raise HTTPException(status_code=404, detail=f"Patient {id} not found")

@router.delete("/{id}", status_code=203)
async def delete_patient(id, current_user: schemas.User = Depends(get_current_user)):
    if current_user.role != Roles.TECHNICIAN or current_user.is_verified == False:
        raise HTTPException(status_code=403, detail='Forbidden! Url is not permitted to this user.')
    delete_result = await collection.delete_one({"_id":id})
    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=[])

    raise HTTPException(status_code=404, detail=f"Patient {id} not found")