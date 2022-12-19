from datetime import timedelta, datetime
from random import choice
from string import digits

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from psycopg2 import sql
from starlette import status

from api.model.shared import get_password_hash, verify_password
from api.model.user import UserCreate, User
from api.settings import Settings

ACCESS_TOKEN_EXPIRE_MINUTES = 30


class UserController:
    def __init__(self, cursor, settings: Settings):
        self.cursor = cursor
        self.settings = settings

    def get_user_by_email(self, email: str) -> User:
        """
        Query the database to get the user based on his email
        :param email:
        :return: User
        """
        query = sql.SQL("select * from {table} where email={value}").format(
            table=sql.Identifier("user"), value=sql.Literal(email)
        )
        self.cursor.execute(query)
        response = self.cursor.fetchone()
        return User(
            id=response[0],
            email_address=response[1],
            password=response[2],
            is_active=response[3],
        )

    @staticmethod
    def generate_activation_code() -> str:
        """
        Generate and return a 4 digit code
        :return: A 4 digit string code
        """
        return "".join(choice(digits) for _ in range(4))

    @staticmethod
    def send_email_to_user(user: User, activation_code: str):
        """
        Mock function that simulate a SMTP server by printing to the standard output a 4 digit code
        :param user:
        :param activation_code:
        :return: None
        """
        print(
            f"""
            to: {user.email_address}
            subject: Activation code Dailymotion:
            Hello, here is your activation code : {activation_code}
        """
        )  # This print is here to "mock" the smtp server

    def create_user(self, user_create: UserCreate) -> User:
        """
        Create a user, store it to the database and return it
        :param user_create: A UserCreate Object with everything needed to create a User in database
        :return: User object
        """
        user_create.password = get_password_hash(user_create.password)
        self.cursor.execute(
            sql.SQL(
                "INSERT INTO {} (email, password, is_active) VALUES (%s, %s, %s) RETURNING id"
            ).format(sql.Identifier("user")),
            [user_create.email_address, user_create.password, False],
        )
        user_id = self.cursor.fetchone()[0]
        activation_code = self.generate_activation_code()
        self.cursor.execute(
            sql.SQL(
                "INSERT INTO {} (user_id, activation_code) VALUES (%s, %s)"
            ).format(sql.Identifier("user_activation")),
            [user_id, activation_code],
        )
        user = User(
            id=user_id,
            email_address=user_create.email_address,
            password=user_create.password,
            is_active=False,
        )
        self.send_email_to_user(user, activation_code)
        return user

    def get_user_activation_code(self, user_id: int):
        """
        Get a user activation code based on his id
        :param user_id: id of a user
        :return: All the fields inside the user_activation table
        """
        query = sql.SQL(
            "select {fields} from {table} where user_id={value}"
        ).format(
            fields=sql.SQL(",").join(
                [
                    sql.Identifier("user_id"),
                    sql.Identifier("activation_code"),
                    sql.Identifier("created_at"),
                ]
            ),
            table=sql.Identifier("user_activation"),
            value=sql.Literal(user_id),
        )
        self.cursor.execute(query)
        response = self.cursor.fetchone()
        if response is None:
            raise HTTPException(
                status_code=404,
                detail=f"Couldn't find user with id '{user_id}'",
            )
        return response

    def authenticate_user(
        self, email_address: str, password: str
    ) -> User | None:
        """
        Check if user has correct password and if user is active
        :param email_address: email address of the user
        :param password: password of the user
        :return: User if we can retrieve user from its email and if user is active and if the password match the user's one.
        """
        user = self.get_user_by_email(email_address)
        if (
            not user
            or user.is_active is False
            or not verify_password(password, user.password)
        ):
            return None
        return user

    def create_access_token(
        self, data: dict, expires_delta: timedelta | None = None
    ) -> str:
        """
        Create a JWT Token
        :param data:
        :param expires_delta:
        :return: An encoded jwt token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            self.settings.secret_key,
            algorithm=self.settings.algorithm,
        )
        return encoded_jwt

    def login_user(self, form_data: OAuth2PasswordRequestForm):
        """
        Authenticate user
        :param form_data:
        :return: An access token
        """
        user = self.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.email_address},
            expires_delta=access_token_expires,
        )
        return {"access_token": access_token, "token_type": "bearer"}

    def activate_user(self, email_address: str, activation_code: str):
        """

        :param email_address:
        :param activation_code:
        :return:
        """
        user = self.get_user_by_email(email_address)
        if user.is_active is True:
            raise HTTPException(
                status_code=409, detail="User already registered"
            )
        _, activation_code_db, created_at = self.get_user_activation_code(
            user.id
        )
        if (datetime.now() - created_at).total_seconds() > 60:
            new_code = self.generate_activation_code()
            self.cursor.execute(
                sql.SQL(
                    "UPDATE {table} SET activation_code = {activation_code}, created_at = {created_at} where user_id={value}"
                ).format(
                    table=sql.Identifier("user_activation"),
                    value=sql.Literal(user.id),
                    activation_code=sql.Literal(new_code),
                    created_at=sql.Literal(datetime.now()),
                )
            )
            self.send_email_to_user(user, new_code)
            raise HTTPException(status_code=409, detail="The code is outdated")
        if activation_code == activation_code_db:
            self.cursor.execute(
                sql.SQL(
                    "UPDATE {table} SET is_active = true where id={value}"
                ).format(
                    table=sql.Identifier("user"), value=sql.Literal(user.id)
                )
            )
        else:
            raise HTTPException(
                status_code=409, detail="Wrong activation code"
            )
