from datetime import datetime, timedelta, timezone

from flask import Blueprint, request, jsonify, current_app
from redis import Redis
from rq import Queue

from app import db
from app.models import Task
from app.schemas import TaskSchema, TaskUpdateSchema, TaskResponseSchema
from app.jobs import send_due_date_notification

tasks_bp = Blueprint("tasks", __name__)

task_schema = TaskSchema()
task_update_schema = TaskUpdateSchema()
task_response_schema = TaskResponseSchema()
tasks_response_schema = TaskResponseSchema(many=True)


def _get_queue():
    redis_url = current_app.config["REDIS_URL"]
    conn = Redis.from_url(redis_url)
    return Queue(connection=conn)


def _should_queue_notification(due_date):
    if due_date is None:
        return False
    now = datetime.now(timezone.utc)
    # Ensure due_date is timezone-aware
    if due_date.tzinfo is None:
        due_date = due_date.replace(tzinfo=timezone.utc)
    return now < due_date <= now + timedelta(hours=24)


@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    query = db.select(Task)

    completed_param = request.args.get("completed")
    if completed_param is not None:
        if completed_param.lower() == "true":
            query = query.filter_by(completed=True)
        elif completed_param.lower() == "false":
            query = query.filter_by(completed=False)

    tasks = db.session.execute(query).scalars().all()
    return jsonify({"tasks": tasks_response_schema.dump(tasks)}), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task_response_schema.dump(task)), 200


@tasks_bp.route("/tasks", methods=["POST"])
def create_task():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"errors": {"json": ["No input data provided."]}}), 400

    errors = task_schema.validate(json_data)
    if errors:
        return jsonify({"errors": errors}), 400

    data = task_schema.load(json_data)
    task = Task(**data)
    db.session.add(task)
    db.session.commit()

    notification_queued = False
    if _should_queue_notification(task.due_date):
        try:
            q = _get_queue()
            q.enqueue(send_due_date_notification, task.id, task.title)
            notification_queued = True
        except Exception:
            pass

    result = task_response_schema.dump(task)
    result["notification_queued"] = notification_queued
    return jsonify({"task": result, "notification_queued": notification_queued}), 201


@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    json_data = request.get_json()
    if not json_data:
        return jsonify({"errors": {"json": ["No input data provided."]}}), 400

    errors = task_update_schema.validate(json_data)
    if errors:
        return jsonify({"errors": errors}), 400

    data = task_update_schema.load(json_data)
    for key, value in data.items():
        setattr(task, key, value)

    db.session.commit()
    return jsonify(task_response_schema.dump(task)), 200


@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200
