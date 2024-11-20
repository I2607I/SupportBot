from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import INTEGER, TEXT, TIMESTAMP, UUID
from sqlalchemy.sql import func

from project.db import DeclarativeBase


class TgUsers(DeclarativeBase):
    __tablename__ = "tg_users"  

    tg_user = Column(
        INTEGER,
        primary_key=True,
        unique=True,
        doc="Unique id of the string in table",
    )
    back_user = Column(
        UUID(as_uuid=True),
        unique=True,
    )
