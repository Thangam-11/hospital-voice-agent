from pydantic import BaseModel, EmailStr, Field

class AuthRegisterRequest(BaseModel):
    email:EmailStr
    user_name : str = Field(min_length=3, max_length=50)
    full_name : str = Field(min_length=3, max_length=50)
    password : str =  Field(min_length=8, max_length=128)

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class AdminResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool
class AdminResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool


class AdminLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: AdminResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str