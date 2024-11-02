from pydantic import BaseModel, Field
from typing import Optional, List
import re

class EmployeeSchema(BaseModel):
    employee_id: str = Field(None, pattern=r"^[a-zA-Z0-9]*+$")
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    gender: str = Field(None, pattern=r"^M|F$")
    isadmin: str = Field(None, pattern=r"^N|Y$")
    name: str = Field(None, pattern=r"^[a-zA-Z0-9\s]+$")
    department: str = Field(..., pattern=r"^HR|Engineering|Sales$")
    role: str = Field(..., pattern=r"^Manager|Developer|Analyst$")
    
class EmployeeSchemaAttributes(BaseModel):
    employee_data: EmployeeSchema
    
class EmployeeSchemaGetData(BaseModel):
    message: EmployeeSchema

class ArrayEmployeeSchemaGetData(BaseModel):
    message: List[EmployeeSchema]
    
class SuccessResponse(BaseModel):
    message: str

class BadRequestResponse(BaseModel):
    message: str

class NotFoundResponse(BaseModel):
    message: str
    
class InternalServerError(BaseModel):
    message: str