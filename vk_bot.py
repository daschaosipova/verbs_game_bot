import logging
import os
import vk_api

from dotenv import load_dotenv
from vk_api.longpoll import VkLongPoll, VkEventType

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main() -> None:
    load_dotenv()
    vk_token = os.getenv("VK_TOKEN")

    vk_session = vk_api.VkApi(token=vk_token)
    longpoll = VkLongPoll(vk_session)

    logger.info("VK-бот успешно запущен и слушает сервер...")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                logger.info(f"Новое сообщение для меня от {event.user_id}: {event.text}")
            else:
                logger.info(f"Новое сообщение от меня для {event.user_id}: {event.text}")


if __name__ == "__main__":
    main()