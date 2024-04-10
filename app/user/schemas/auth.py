from pydantic import BaseModel, EmailStr, Field


class RegistrationIn(BaseModel):
    email: EmailStr = Field(..., description="Email")
    full_name: str = Field(..., description="Full Name")
    password: str = Field(..., description="Password")


class LoginIn(BaseModel):
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., description="Password")


class RefreshTokenIn(BaseModel):
    refresh_token: str = Field(..., description="Refresh Token")


class PasswordChangeIn(BaseModel):
    old_password: str = Field(..., description="Old Password")
    new_password: str = Field(..., description="New Password")


class ForgotPasswordRequestIn(BaseModel):
    email: EmailStr = Field(..., description="Email")
