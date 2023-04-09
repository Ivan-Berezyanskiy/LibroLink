from celery import shared_task

from library_service.settings import TELEGRAM_BOT
from library_service.settings import TELEGRAM_CHAT_ID


@shared_task
def send_message(validated_data: dict) -> None:
    """ Send message to admin(create borrowing, return borrowing) """
    data = f"vsdasdasdasdy"
    TELEGRAM_BOT.send_message(text=data, chat_id=TELEGRAM_CHAT_ID)
