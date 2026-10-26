from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

metadata = MetaData(schema="app")

class Base(DeclarativeBase):
    metadata = metadata

from models import (
    login_log,
)# noqa: F401
