"""
Configuration and preparation of SQLAlchemy tools.
"""
from typing import Type

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from configs import config


# Private factory:
def _make_session_class() -> Type[Session]:
    engine = create_engine(config.DATABASE_URI)
    return sessionmaker(bind=engine)


_session_class = _make_session_class()


# Public tools:
def new_session() -> Session:
    return _session_class()
