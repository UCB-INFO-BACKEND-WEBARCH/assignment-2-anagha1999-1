import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_due_date_notification(task_id, task_title):
    """Simulate sending a notification for a task due soon."""
    time.sleep(5)
    logger.info("Reminder: Task '%s' is due soon!", task_title)
