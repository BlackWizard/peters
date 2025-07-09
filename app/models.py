from datetime import datetime

from sqlalchemy import func, Column
from sqlalchemy.orm import declared_attr

from fastapi_storages import FileSystemStorage
from fastapi_storages.integrations.sqlalchemy import FileType, ImageType


from sqlmodel import SQLModel, Field, Relationship


storage = FileSystemStorage(path="/nfs/dvr/plates")

class DBModel(SQLModel):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"


class BaseModel(DBModel):
    id: int = Field(
        primary_key=True,
        index=True,
        nullable=False,
    )
    updated_at: datetime | None = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": func.now(), "onupdate": datetime.utcnow}
    )
    created_at: datetime | None = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": func.now()},
    )


class AuthorBase(SQLModel):
    name: str = Field(index=True)
    short: str | None = Field(index=True, nullable=True)


class Author(BaseModel, AuthorBase, table=True):
    titles: list["Title"] = Relationship(
        back_populates="author", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"short={self.short!r}, "
            f"name={self.name!r})"
        )

class TitleBase(SQLModel):
    name: str = Field(index=True)
    code: str = Field(index=True)
    year: int | None = None
    pages: int | None = None
    author_id: int = Field(foreign_key="authors.id")
    logo: ImageType = Field(default=None, sa_column=Column(ImageType(storage=storage)))

class Title(BaseModel, TitleBase, table=True):
    author: Author = Relationship(
        back_populates="titles", sa_relationship_kwargs={"lazy": "selectin"}
    )
    files: list["File"] = Relationship(  # noqa: F821
        back_populates="title", sa_relationship_kwargs={"lazy": "selectin"}
    )
    plates: list["TitlePlate"] = Relationship(  # noqa: F821
        back_populates="title", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"author_id={self.author_id!r}, "
            f"name={self.name!r})"
        )


class  TitlePlateBase(SQLModel):
    title_id: int = Field(foreign_key="titles.id", nullable=False)
    plate: int
    position: int = Field(default=1)

class TitlePlate(BaseModel, TitlePlateBase, table=True):
    title: Title = Relationship(
        back_populates="plates", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"title_id={self.title_id!r}, "
            f"plate={self.plate!r})"
        )


class SourceBase(SQLModel):
    name: str = Field(index=True)
    url: str | None = None


class Source(BaseModel, SourceBase, table=True):
    files: list["File"] = Relationship(  # noqa: F821
        back_populates="source", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"name={self.name!r}, "
            f"url={self.url!r})"
        )

class FileBase(SQLModel):
    title_id: int = Field(foreign_key="titles.id")
    source_id: int = Field(foreign_key="sources.id")
    file: FileType = Field(sa_column=Column(FileType(storage=storage)))
    url: str | None = None

class File(BaseModel, FileBase, table=True):
    title: Title = Relationship(
        back_populates="files", sa_relationship_kwargs={"lazy": "selectin"}
    )
    source: Source = Relationship(
        back_populates="files", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"file={self.file.name!r})"
        )
