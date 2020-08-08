"""
Configuration and preparation of SQLAlchemy tools.
"""
from typing import Type

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from configs import SQLITE_FILE_NAME


# Private factory:
def _make_session_class() -> Type[Session]:
    db_uri = f"sqlite:///{SQLITE_FILE_NAME}"
    engine = create_engine(db_uri)
    return sessionmaker(bind=engine)


_session_class = _make_session_class()


# Public tools:
def new_session() -> Session:
    return _session_class()
