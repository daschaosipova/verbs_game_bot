import logging
import sys

import telegram


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.tg_bot = tg_bot
        self.chat_id = chat_id

    def emit(self, record):
        if (
            record.name.startswith("telegram")
            or record.name.startswith("urllib3")
            or record.name.startswith("requests")
        ):
            return
        log_entry = self.format(record)
        try:
            self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)
        except telegram.error.TelegramError as err:
            sys.stderr.write(f"Не удалось отправить лог в Telegram: {err}\n")


def configure_logging(tg_token, chat_id):
    """Настраивает логирование в консоль и отправку ошибок в Telegram."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    tg_bot = telegram.Bot(token=tg_token)
    tg_handler = TelegramLogsHandler(tg_bot=tg_bot, chat_id=chat_id)
    tg_handler.setLevel(logging.ERROR)
    logging.getLogger().addHandler(tg_handler)
