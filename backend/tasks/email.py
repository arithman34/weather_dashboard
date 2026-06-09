from backend.celery_app import celery
from backend.services.email import send_email


@celery.task(name="backend.tasks.email.send_welcome_email")
def send_welcome_email(username: str, email: str) -> None:
    send_email(username=username, email=email)
