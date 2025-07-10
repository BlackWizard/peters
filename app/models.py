import contextlib
import os
from datetime import datetime

from pydantic import BaseModel

# from libcloud.storage.drivers.local import LocalStorageDriver
from libcloud.storage.providers import get_driver
from libcloud.storage.types import (
    ContainerAlreadyExistsError,
    # ObjectDoesNotExistError,
    Provider,
)

from sqlalchemy import func, Column
from sqlalchemy.orm import declared_attr
from sqlalchemy_file import File, FileField, ImageField
# from sqlalchemy_file.exceptions import ValidationError
from sqlalchemy_file.storage import StorageManager
from sqlalchemy_file.validators import SizeValidator

from fastapi import Form, UploadFile
from fastapi import File as FormFile
# from fastapi_storages import FileSystemStorage
# from fastapi_storages.integrations.sqlalchemy import FileType, ImageType
from sqlalchemy_file import File, FileField, ImageField


from sqlmodel import SQLModel, Field, Relationship


# storage = FileSystemStorage(path="/nfs/dvr/plates")

os.makedirs("/nfs/dvr/plates/", 0o777, exist_ok=True)
driver = get_driver(Provider.LOCAL)("/nfs/dvr/plates")

with contextlib.suppress(ContainerAlreadyExistsError):
    for container_name in ("logo", "file"):
        driver.create_container(container_name=container_name)
        container = driver.get_container(container_name=container_name)

        StorageManager.add_storage(container_name, container)


class Thumbnail(BaseModel):
    path: str
    url: str | None = None


class FileInfo(BaseModel):
    filename: str
    content_type: str
    path: str
    url: str | None = None


class ImageInfo(FileInfo):
    thumbnail: Thumbnail


class DBModel(SQLModel):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"


class DBModelBase(DBModel):
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


class Author(DBModelBase, AuthorBase, table=True):
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
    code: str | None = Field(index=True, nullable=True)
    year: int | None = None
    pages: int | None = None
    author_id: int = Field(foreign_key="authors.id")
    # logo: ImageType = Field(default=None, sa_column=Column(ImageType(storage=storage)))

class Title(DBModelBase, TitleBase, table=True):
    author: Author = Relationship(
        back_populates="titles", sa_relationship_kwargs={"lazy": "selectin"}
    )
    files: list["File"] = Relationship(  # noqa: F821
        back_populates="title", sa_relationship_kwargs={"lazy": "selectin"}
    )
    plates: list["TitlePlate"] = Relationship(  # noqa: F821
        back_populates="title", sa_relationship_kwargs={"lazy": "selectin"}
    )

    logo: File | UploadFile | None = Field(
        sa_column=Column(
            ImageField(
                upload_storage="logo",
                thumbnail_size=(300, 430),
                validators=[SizeValidator(max_size="1M")],
            )
        )
    )

    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"author_id={self.author_id!r}, "
            f"name={self.name!r})"
        )


class TitleOut(TitleBase):
    logo: ImageInfo | None = None


def title_form(
    name: str = Form(..., min_length=3),
    logo: UploadFile | None = FormFile(None),
):
    return Title(name=name, image=image)


class  TitlePlateBase(SQLModel):
    title_id: int = Field(foreign_key="titles.id", nullable=False)
    plate: int
    position: int = Field(default=1)

class TitlePlate(DBModelBase, TitlePlateBase, table=True):
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


class Source(DBModelBase, SourceBase, table=True):
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
    # file: FileType = Field(sa_column=Column(FileType(storage=storage)))
    url: str | None = None


class File(DBModelBase, FileBase, table=True):
    title: Title = Relationship(
        back_populates="files", sa_relationship_kwargs={"lazy": "selectin"}
    )
    source: Source = Relationship(
        back_populates="files", sa_relationship_kwargs={"lazy": "selectin"}
    )

    file: File | UploadFile | None = Field(
        sa_column=Column(
            FileField(
                upload_storage="file",
                validators=[SizeValidator(max_size="1G")],
            )
        )
    )
    class Config:
        arbitrary_types_allowed = True

    def __str__(self):
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"file={self.file!r})"
        )


class FileOut(FileBase):
    file: ImageInfo | None = None
