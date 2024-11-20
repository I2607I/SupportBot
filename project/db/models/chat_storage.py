from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import INTEGER, TEXT, TIMESTAMP, UUID
from sqlalchemy.sql import func
from project.db import DeclarativeBase


class ChatStorage(DeclarativeBase):
    __tablename__ = "chat_storage"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        unique=True,
        doc="Unique id of the string in table",
    )
    user_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        )
    chat_id = Column(
        UUID(as_uuid=True),
        nullable=False,
        )

    sender = Column(
    	TEXT,
    	nullable=False,
    	)
    message = Column(
    	TEXT,
    	nullable=False,
    	)
    dt_created = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
        index = True,
        doc="Date and time when string in table was created",
    )
    grade = Column(
        INTEGER,
        nullable=True,
        )
    accuracy = Column(
        INTEGER,
        nullable=True,
        )
    def __repr__(self):
        columns = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        return f'<{self.__tablename__}: {", ".join(map(lambda x: f"{x[0]}={x[1]}", columns.items()))}>'