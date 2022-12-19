from api.model.shared import DBModel


class UserBase(DBModel):
    email_address: str | None = None


class UserCreate(UserBase):
    password: str


class UserView(UserBase):
    id: int


class User(UserBase):
    id: int | None
    password: str
    is_active: bool
