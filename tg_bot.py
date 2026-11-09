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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Отправляет 'Здравствуйте' при команде /start."""
    update.message.reply_text("Здравствуйте")


def detect_intent_text(
    session_client, project_id, session_id, text, language_code="ru"
):
    """Отправляет текст в Dialogflow и возвращает ответ."""
    session = session_client.session_path(project_id, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    return response.query_result


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


def main() -> None:
    load_dotenv()
    tg_token = os.getenv("TG_TOKEN")
    project_id = os.getenv("PROJECT_ID")
    dialogflow_client = dialogflow.SessionsClient()
    updater = Updater(tg_token, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.bot_data["project_id"] = project_id
    dispatcher.bot_data["session_client"] = dialogflow_client

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, reply_with_dialogflow)
    )

    updater.start_polling()

    logger.info("Бот успешно запущен на Python 3.11 и готов к работе!")
    updater.idle()


if __name__ == "__main__":
    main()
