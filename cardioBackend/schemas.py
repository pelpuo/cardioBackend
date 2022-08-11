from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional
from bson import ObjectId

class Roles:
    DOCTOR = "doctor"
    TECHNICIAN = "technicial"
    ADMIN = "admin"

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    first_name:str
    last_name:str
    email_address:str
    password:str
    isVerified: bool = False
    role: str = Roles.DOCTOR

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "first_name": "Jane",
                "last_name": "Doe",
                "email_address": "jdoe@example.com",
                "password": "password",
            }
        }

class UpdateUser(BaseModel):
    first_name:str
    last_name:str
    email_address:str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "first_name": "Jane",
                "last_name": "Doe",
                "email_address": "jdoe@example.com",
            }
        }


class Patient(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    first_name:str
    last_name:str
    email_address:str
    date_of_birth: str
    gender: str
    doctor_id: str 

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "first_name": "Jane",
                "last_name": "Doe",
                "email_address": "jdoe@example.com",
                "date_of_birth": "dd/mm/yyyy",
                "gender": "male",
                "doctor_id": "123456",
            }
        }


class UpdatePatient(BaseModel):
    first_name:str
    last_name:str
    email_address:str
    date_of_birth: datetime
    gender: str
    doctor_id: int 

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "first_name": "Jane",
                "last_name": "Doe",
                "email_address": "jdoe@example.com",
                "date_of_birth": "",
                "gender": "male",
                "doctor_id": "123456",
            }
        }

class EgcValues(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    reading_id: str
    values: List[Dict] = []

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "reading_id": "123456",
            "values": [
                {
                    "sample": 0,
                    "MLII": 995,
                    "V5": 1011
                },
                {
                    "sample": 1,
                    "MLII": 995,
                    "V5": 1011
                },
                {
                    "sample": 2,
                    "MLII": 995,
                    "V5": 1011
                }
                ]
        }


class Reading(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    patient_id: str
    lead_type:str
    lead_placement:str
    hospital_name:str
    created_at: datetime = datetime.now()
    speed: float
    limb: float
    chest: float
    values: List[Dict]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "patient_id": "123456",
                "hospital_name": "Komfo Anokye Teaching Hospital",
                "lead_type": "12 lead",
                "lead_placement": "standard",
                "speed": 25,
                "limb": 10,
                "chest": 10,
                "values": [
                        {
                            "sample": 0,
                            "MLII": 995,
                            "V5": 1011
                        },
                        {
                            "sample": 1,
                            "MLII": 995,
                            "V5": 1011
                        },
                        {
                            "sample": 2,
                            "MLII": 995,
                            "V5": 1011
                        }
                    ]
            }
        }

class ShowReading(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    patient_id:str
    lead_type:str
    lead_placement:str
    hospital_name:str
    created_at: datetime = datetime.now()
    speed: float
    limb: float
    chest: float
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "patient_id": "123456",
                "hospital_name": "Komfo Anokye Teaching Hospital",
                "lead_type": "12 lead",
                "lead_placement": "standard",
                "speed": 25,
                "limb": 10,
                "chest": 10,
            }
        }

class Login(BaseModel):
    username:str
    password:str

    class Config():
        orm_mode = True

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    id: str
    email: Optional[str] = None
    role: str = None