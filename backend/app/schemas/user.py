from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from backend.app.models.user import UserRole


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentProfileBase(BaseModel):
    standard_id: Optional[str] = None
    division: Optional[str] = None
    enrollment_number: Optional[str] = None


class StudentProfileCreate(StudentProfileBase):
    user_id: str


class StudentProfileResponse(StudentProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeacherProfileBase(BaseModel):
    employee_id: Optional[str] = None


class TeacherProfileCreate(TeacherProfileBase):
    user_id: str


class TeacherProfileResponse(TeacherProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
