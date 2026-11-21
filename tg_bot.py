import logging
import os

from dotenv import load_dotenv
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import dialogflow_v2 as dialogflow
from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

from dialogflow_api import detect_intent_text
from tg_logs_handler import configure_logging

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Отправляет 'Здравствуйте' при команде /start."""
    update.message.reply_text("Здравствуйте")


def reply_with_dialogflow(update: Update, context: CallbackContext) -> None:
    """Получает ответ от DialogFlow и отправляет его пользователю в Telegram."""
    project_id = context.bot_data["project_id"]
    session_client = context.bot_data["session_client"]

    session_id = f"tg_{update.message.chat_id}"
    user_text = update.message.text

    try:
        query_result = detect_intent_text(
            session_client, project_id, session_id, user_text
        )
        update.message.reply_text(query_result.fulfillment_text)
    except GoogleAPICallError as e:
        logger.error(f"Ошибка при работе с Dialogflow API: {e}")


def error_handler(update: object, context: CallbackContext) -> None:
    """Логирует необработанные исключения и отправляет их в Telegram."""
    logger.error("Произошла ошибка в TG-боте:", exc_info=context.error)


def main() -> None:
    load_dotenv()
    tg_token = os.getenv("TG_TOKEN")
    project_id = os.getenv("PROJECT_ID")
    tg_chat_id = os.getenv("TG_CHAT_ID")
    configure_logging(tg_token, tg_chat_id)
    dialogflow_client = dialogflow.SessionsClient()
    updater = Updater(tg_token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.bot_data["project_id"] = project_id
    dispatcher.bot_data["session_client"] = dialogflow_client

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, reply_with_dialogflow)
    )
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()

    logger.info("Бот успешно запущен на Python 3.11 и готов к работе!")
    updater.idle()


if __name__ == "__main__":
    main()
