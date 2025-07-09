from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware, db
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from sqladmin import Admin, ModelView
from sqladmin.filters import ForeignKeyFilter

from app.models import engine, Source, Author, Title, TitlePlate, File
from app.config import ModeEnum, settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    print("startup fastapi")
    yield
    # shutdown


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    SQLAlchemyMiddleware,
    db_url=str(settings.ASYNC_DATABASE_URI),
    engine_args={
        "echo": False,
        "poolclass": NullPool
        if settings.MODE == ModeEnum.testing
        else AsyncAdaptedQueuePool
        # "pool_pre_ping": True,
        # "pool_size": settings.POOL_SIZE,
        # "max_overflow": 64,
    },
)

admin = Admin(app, engine)

app.mount("/static", StaticFiles(directory="static", html=True))
app.mount("/plates", StaticFiles(directory="/nfs/dvr/plates"))

templates = Jinja2Templates(directory='templates')

class SourceAdmin(ModelView, model=Source):
    column_list = [
        Source.id,
        Source.name,
    ]
    column_sortable_list = [
        Source.id,
        Source.name,
    ]
    column_searchable_list = [
        Source.name,
    ]
    form_excluded_columns = [Source.files, Source.created_at, Source.updated_at]


admin.add_view(SourceAdmin)


class AuthorAdmin(ModelView, model=Author):
    column_list = [Author.id, Author.name, Author.short]
    column_sortable_list = [Author.id, Author.name, Author.short]
    column_searchable_list = [Author.name, Author.short]
    form_excluded_columns = [Author.titles, Author.created_at, Author.updated_at]


admin.add_view(AuthorAdmin)


class TitleAdmin(ModelView, model=Title):
    column_list = [Title.id, Title.name, Title.author]
    form_excluded_columns = [Title.created_at, Title.updated_at]

    form_ajax_refs = {
        "plates": {
            "fields": ("id", "plate"),
            "order_by": "id",
        },
        "files": {
            "fields": ("id",),
            "order_by": "id",
        },

    }

#    column_filters = [
#        ForeignKeyFilter(Author.id, Author.short, title="Author")
#    ]


admin.add_view(TitleAdmin)


class TitlePlateAdmin(ModelView, model=TitlePlate):
    column_list = [TitlePlate.id, TitlePlate.plate, TitlePlate.position, TitlePlate.title]
    form_excluded_columns = [TitlePlate.created_at, TitlePlate.updated_at]

    form_ajax_refs = {
        "title": {
            "fields": ("id", "name"),
            "order_by": "id",
        },
    }

admin.add_view(TitlePlateAdmin)


class FileAdmin(ModelView, model=File):
    column_list = [File.id, File.title, File.source]
    form_excluded_columns = [File.created_at, File.updated_at]

    form_ajax_refs = {
        "title": {
            "fields": ("id", "name"),
            "order_by": "id",
        },
    }


admin.add_view(FileAdmin)


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})
