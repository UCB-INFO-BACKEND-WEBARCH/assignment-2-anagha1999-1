from flask import Blueprint, request, jsonify

from app import db
from app.models import Category
from app.schemas import (
    CategorySchema,
    CategoryResponseSchema,
    CategoryDetailSchema,
)

categories_bp = Blueprint("categories", __name__)

category_schema = CategorySchema()
category_response_schema = CategoryResponseSchema(many=True)
category_detail_schema = CategoryDetailSchema()


@categories_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = db.session.execute(db.select(Category)).scalars().all()
    result = []
    for cat in categories:
        result.append(
            {
                "id": cat.id,
                "name": cat.name,
                "color": cat.color,
                "task_count": cat.tasks.count(),
            }
        )
    return jsonify({"categories": result}), 200


@categories_bp.route("/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    return jsonify(category_detail_schema.dump(category)), 200


@categories_bp.route("/categories", methods=["POST"])
def create_category():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"errors": {"json": ["No input data provided."]}}), 400

    errors = category_schema.validate(json_data)
    if errors:
        return jsonify({"errors": errors}), 400

    data = category_schema.load(json_data)
    category = Category(**data)
    db.session.add(category)
    db.session.commit()

    return (
        jsonify({"id": category.id, "name": category.name, "color": category.color}),
        201,
    )


@categories_bp.route("/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    if category.tasks.count() > 0:
        return (
            jsonify(
                {
                    "error": "Cannot delete category with existing tasks. Move or delete tasks first."
                }
            ),
            400,
        )

    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted"}), 200
