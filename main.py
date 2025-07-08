from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.filters import ForeignKeyFilter

from app.models import engine, Source, Author, Title, TitlePlate, File

app = FastAPI()
admin = Admin(app, engine)


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
