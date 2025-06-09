from pydantic import BaseModel, EmailStr, Field, validator, root_validator
import re
from .user.pswd_validation_str import pswd_validation_str

class RegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str

    @root_validator(pre=True) # type: ignore
    def validate_values(cls, values):
        if len(values.keys()) != 3:
            raise ValueError("incorrect number of fields provided")
        if 'email' not in values or 'password' not in values or 'confirm_password' not in values:
            raise ValueError("Missing required fields: 'email', 'password', and 'confirm_password' are required.")
        return values

    @validator("password")
    def password_complexity(cls, v):
        if not re.fullmatch(pswd_validation_str, v):
            raise ValueError("Passwords must be a minimum of 8 characters long, contain at least one uppercase letter, one number, and one special character.")
        return v
    
    @validator("confirm_password")
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError("Passwords do not match.")
        return v
    

class VerifyEmailSchema(BaseModel):
    token: str

@root_validator(pre=True)
def validate_body(cls, values):
    if values.keys() != 1:
        raise ValueError("incorrect number of field provided")
    if "token" not in values:
        raise ValueError("Missing required field: token")
    return values

class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


@root_validator(pre=True)
def validate_body(cls, values):
    if values.keys() != 2:
        raise ValueError("incorrect number of field provided")
    elif "email" not in values or "password" not in values:
        raise ValueError("Missing required fields: 'email', 'password' are required.")
    
@validator("password")
def validate_password(cls, v):
    if not re.fullmatch(pswd_validation_str, v):
        raise ValueError("Passwords must be a minimum of 8 characters long, contain at least one uppercase letter, one number, and one special character.")
    return v