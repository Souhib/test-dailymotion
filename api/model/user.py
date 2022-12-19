from api.model.shared import DBModel


class UserBase(DBModel):
    """
    Class used for heritage

    Attributes
    ----------
    email_address : str
        An email_address
    """
    email_address: str | None = None


class UserCreate(UserBase):
    """
    Class used by the router to get from the client his email and password

    Attributes
    ----------
    password : str
        A plain password send by the client
    """
    password: str


class UserView(UserBase):
    """
    Class used by the router to send a response to the user

    Attributes
    ----------
    id : int
        The id of the user in the database
    """
    id: int


class User(UserBase):
    """
    Class used inside the controller to create a new user in the database

    Attributes
    ----------
    id : int
        The id of the user in the database
    password : str
        The hashed password that will be stored in the database
    is_active : bool
        boolean that tells whether a user is active
    """
    id: int | None
    password: str
    is_active: bool
