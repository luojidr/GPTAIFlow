import os.path
import urllib.parse
from typing import Union

from flask import Flask, current_app
from flask.helpers import get_debug_flag
from flask_sqlalchemy import SQLAlchemy

__all__ = ["init_db_extension"]


def init_db_extension(app: Flask) -> SQLAlchemy:
    params = {
        "user": os.environ.get("MYSQL_USER"),
        "pwd": os.environ.get("MYSQL_PASSWORD"),
        "host": os.environ.get("MYSQL_HOST"),
        "port": os.environ.get("MYSQL_PORT", "3306"),
        "database": None
    }

    if "@" in params["pwd"]:
        params["pwd"] = urllib.parse.quote_plus(params["pwd"])

    # maybe raise 'RuntimeError' to outside app context
    # app = app or current_app._get_current_object()

    if "SQLALCHEMY_DATABASE_URI" in app.config:
        raise RuntimeError("'SQLALCHEMY_DATABASE_URI' cannot be allow to set.")

    if get_debug_flag():
        app.config["SQLALCHEMY_ECHO"] = True

    app.config["SQLALCHEMY_POOL_SIZE"] = 10
    app.config["SQLALCHEMY_POOL_TIMEOUT"] = 10
    app.config["SQLALCHEMY_POOL_RECYCLE"] = 3600
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}".format(**params)
    app.config["SQLALCHEMY_BINDS"] = {
        "compression": "mysql+pymysql://{user}:{pwd}@{host}:{port}/db_compression".format(**params)
    }

    app.logger.info("Compression SQLALCHEMY_DATABASE_URI: %s", app.config["SQLALCHEMY_DATABASE_URI"])
    app.logger.info("Compression SQLALCHEMY_BINDS: %s", app.config["SQLALCHEMY_BINDS"])
    return SQLAlchemy(app)

