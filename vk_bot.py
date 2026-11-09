import logging
import os
import random
import vk_api as vk

from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def echo(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        random_id=random.randint(1,1000)
    )


def main() -> None:
    load_dotenv()
    vk_token = os.getenv("VK_TOKEN")

    vk_session = vk.VkApi(token=vk_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    logger.info("VK-бот успешно запущен и слушает сервер...")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                logger.info(f"Новое сообщение для меня от {event.user_id}: {event.text}")
                echo(event, vk_api)
            else:
                logger.info(f"Новое сообщение от меня для {event.user_id}: {event.text}")


if __name__ == "__main__":
    main()