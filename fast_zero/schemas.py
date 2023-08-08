from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    name: str
    email: EmailStr


class UserDB(User):
    id: int


class UserList(BaseModel):
    users: list[UserPublic]
