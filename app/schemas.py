import re
from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models import Category
from app import db


class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True, validate=validate.Length(min=1, max=50)
    )
    color = fields.Str(
        load_default=None,
        validate=validate.Regexp(
            r"^#[0-9A-Fa-f]{6}$", error="Must be a valid hex color code (e.g., #FF5733)."
        ),
    )

    @validates("name")
    def validate_unique_name(self, value, **kwargs):
        existing = db.session.execute(
            db.select(Category).filter_by(name=value)
        ).scalar_one_or_none()
        if existing:
            raise ValidationError("Category with this name already exists.")


class CategoryResponseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    color = fields.Str()
    task_count = fields.Int()


class CategoryDetailSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    color = fields.Str()
    tasks = fields.List(fields.Nested(lambda: TaskBriefSchema()))


class TaskBriefSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    completed = fields.Bool()


class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(
        required=True, validate=validate.Length(min=1, max=100)
    )
    description = fields.Str(
        load_default=None, validate=validate.Length(max=500)
    )
    completed = fields.Bool(load_default=False)
    due_date = fields.DateTime(format="iso", load_default=None)
    category_id = fields.Int(load_default=None)
    created_at = fields.DateTime(format="iso", dump_only=True)
    updated_at = fields.DateTime(format="iso", dump_only=True)

    @validates("category_id")
    def validate_category_exists(self, value, **kwargs):
        if value is not None:
            category = db.session.get(Category, value)
            if not category:
                raise ValidationError("Category not found.")


class TaskUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    completed = fields.Bool()
    due_date = fields.DateTime(format="iso")
    category_id = fields.Int(allow_none=True)

    @validates("category_id")
    def validate_category_exists(self, value, **kwargs):
        if value is not None:
            category = db.session.get(Category, value)
            if not category:
                raise ValidationError("Category not found.")


class TaskResponseSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    completed = fields.Bool()
    due_date = fields.DateTime(format="iso")
    category_id = fields.Int()
    category = fields.Nested(CategoryResponseSchema, exclude=("task_count",), dump_default=None)
    created_at = fields.DateTime(format="iso")
    updated_at = fields.DateTime(format="iso")
