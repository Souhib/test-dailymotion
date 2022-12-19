import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from api.settings import settings

connection = psycopg2.connect(dbname=settings.db_name, user=settings.db_username, password=settings.db_password, port=settings.db_port, host=settings.db_host)
connection.autocommit = True
connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)


def create_tables():
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS "user" (id SERIAL PRIMARY KEY NOT NULL, email VARCHAR(256), password VARCHAR(256), is_active BOOLEAN);""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS "user_activation" (user_id INT PRIMARY KEY NOT NULL, activation_code VARCHAR(4), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES "user" (id));""")
    cursor.close()


def create_database():
    cursor = connection.cursor()
    try:
        database_name = "Dailymotion"
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
        cursor.close()
    except psycopg2.errors.DuplicateDatabase:
        cursor.close()