from datetime import datetime
from typing import Annotated

from sqlalchemy import ForeignKey, func, String
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)

from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import FileType, ImageType


from app.config import settings

engine = create_async_engine(str(settings.pg_dsn))
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
storage = FileSystemStorage(path="/nfs/dvr/plates")


int_pk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[
    datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)
]
str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
str_null_true = Annotated[str, mapped_column(nullable=True)]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    id: Mapped[int_pk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


class Author(Base):
    name: Mapped[str]
    short: Mapped[str_null_true]

    titles = relationship("Title")
    # titles = relationship('User', secondary='project_users', back_populates='projects')

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"short={self.short!r}, "
            f"name={self.name!r})"
        )


class Title(Base):
    name: Mapped[str]
    code: Mapped[str_null_true]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"), nullable=False)
    year: Mapped[int] = mapped_column(nullable=True)
    pages: Mapped[int] = mapped_column(nullable=True)
    logo = mapped_column(ImageType(storage=storage))

    author: Mapped["Author"] = relationship("Author", back_populates="titles")
    plates = relationship("TitlePlate")
    files = relationship("File")

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"author_id={self.author_id!r}, "
            f"name={self.name!r})"
        )


class TitlePlate(Base):
    title_id: Mapped[int] = mapped_column(ForeignKey("titles.id"), nullable=False)
    plate: Mapped[int]
    position: Mapped[int]

    title: Mapped["Title"] = relationship("Title", back_populates="plates")

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"title_id={self.title_id!r}, "
            f"plate={self.plate!r})"
        )


class Source(Base):
    name: Mapped[str]
    url: Mapped[str]

    files = relationship("File")

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"name={self.name!r}, "
            f"url={self.url!r})"
        )

class File(Base):
    title_id: Mapped[int] = mapped_column(ForeignKey("titles.id"), nullable=False)
    title: Mapped["Title"] = relationship("Title", back_populates="files")
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    source: Mapped["Source"] = relationship("Source", back_populates="files")
    file = mapped_column(FileType(storage=storage))
    url: Mapped[str_null_true]

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"file={self.file.name!r})"
        )
