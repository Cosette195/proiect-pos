import os
from peewee import MySQLDatabase

db = MySQLDatabase(database = os.environ.get("DB_NAME", "idm"),
                   user = os.environ.get("DB_USER", "root"),
                   password = os.environ["DB_PASSWORD"],
                   host = os.environ.get("DB_HOST", "127.0.0.1"),
                   port = int(os.environ.get("DB_PORT", "3306")))