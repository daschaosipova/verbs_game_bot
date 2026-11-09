import logging
import os
import random

import vk_api as vk
from dotenv import load_dotenv
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import dialogflow_v2 as dialogflow
from vk_api.longpoll import VkEventType, VkLongPoll

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


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


def reply_with_dialogflow(event, vk_api, session_client, project_id):
    """Получает ответ от DialogFlow и отправляет его пользователю в VK."""
    session_id = f"vk_{event.user_id}"

    try:
        query_result = detect_intent_text(
            session_client, project_id, session_id, event.text
        )

        if query_result.intent.is_fallback:
            logger.info(f"Фраза не распознана (is_fallback). Бот молчит, уступая оператору.")
            return
        
        vk_api.messages.send(
            user_id=event.user_id,
            message=query_result.fulfillment_text,
            random_id=random.randint(1, 1000),
        )
    except GoogleAPICallError as e:
        logger.error(f"Ошибка при работе с Dialogflow API: {e}")


def main() -> None:
    load_dotenv()
    vk_token = os.getenv("VK_TOKEN")
    project_id = os.getenv("PROJECT_ID")

    dialogflow_client = dialogflow.SessionsClient()

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    logger.info("VK-бот успешно запущен и слушает сервер...")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                logger.info(
                    f"Новое сообщение для меня от {event.user_id}: {event.text}"
                )
                reply_with_dialogflow(event, vk_api, dialogflow_client, project_id)
            else:
                logger.info(
                    f"Новое сообщение от меня для {event.user_id}: {event.text}"
                )


if __name__ == "__main__":
    main()
