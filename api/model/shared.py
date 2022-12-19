from passlib.context import CryptContext
from pydantic import Extra, BaseModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class DBModel(BaseModel):
    class Config:
        extra = Extra.forbid


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email_address: str


def verify_password(plain_password, hashed_password) -> bool:
    """
    It takes a plain text password and a hashed password and returns True if the plain text password matches the hashed
    password

    :param plain_password: The password in plain text that you want to verify
    :param hashed_password: The hashed password that you want to verify
    :return: A boolean value.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    It takes a password and returns a hash of that password

    :param password: The password to be hashed
    :return: The password hash.
    """
    return pwd_context.hash(password)
