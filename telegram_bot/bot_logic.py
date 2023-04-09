import telegram
from celery import shared_task
from datetime import date
from library_service.settings import BOT_TOKEN
from library_service.settings import TELEGRAM_CHAT_ID


@shared_task
async def send_message(
        borrow_date: date.today,
        expected_return_date: date.today,
        book_title: str,
        type_message: str,
) -> None:
    """ Send message to admin(create borrowing, return borrowing) """
    telegram_bot = telegram.Bot(BOT_TOKEN)
    data = type_message + f" borrow_date: {borrow_date} " \
                          f"expected_return_date: {expected_return_date} " \
                          f"book_title: {book_title}"
    await telegram_bot.send_message(text=data, chat_id=TELEGRAM_CHAT_ID)
