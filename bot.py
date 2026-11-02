import logging
import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Обработчик команды /start — отвечает "Здравствуйте" по требованию Devman
def start(update: Update, context: CallbackContext) -> None:
    """Отправляет 'Здравствуйте' при команде /start."""
    update.message.reply_text('Здравствуйте')

# Обработчик команды /help
def help_command(update: Update, context: CallbackContext) -> None:
    """Отправляет сообщение при команде /help."""
    update.message.reply_text('Help!')

# Обработчик эхо-сообщений — повторяет текст пользователя
def echo(update: Update, context: CallbackContext) -> None:
    """Повторяет текстовые сообщения пользователя."""
    update.message.reply_text(update.message.text)

def main() -> None:
    """Запуск бота."""
    load_dotenv()
    tg_token = os.getenv("TOKEN")
    
    # Создаем Updater (на Python 3.11 планировщик ломаться не будет)
    updater = Updater(tg_token, use_context=True)

    # Диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Регистрация команд и сообщений
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Старт поллинга
    updater.start_polling()
    
    logger.info("Бот успешно запущен на Python 3.11 и готов к работе!")
    updater.idle()

if __name__ == '__main__':
    main()
