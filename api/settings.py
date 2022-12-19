from pydantic import BaseSettings


class Settings(BaseSettings):
    encryption_key: str
    db_host: str
    db_name: str
    db_username: str
    db_password: str
    db_port: str
    secret_key: str
    algorithm: str

    class Config:
        env_prefix = ""
        case_sentive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
