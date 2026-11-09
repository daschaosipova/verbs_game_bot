import json
import logging
import os

from dotenv import load_dotenv
from google.cloud import dialogflow_v2 as dialogflow

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    """Создает интент в Dialogflow по API."""
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)

    training_phrases = []
    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        training_phrase = dialogflow.Intent.TrainingPhrase(
            parts=[part], type_=dialogflow.Intent.TrainingPhrase.Type.EXAMPLE
        )
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message],
    )

    response = intents_client.create_intent(
        request={"parent": parent, "intent": intent}
    )

    logger.info(f'Интент "{response.display_name}" успешно создан.')


def main():
    load_dotenv()
    project_id = os.getenv("PROJECT_ID")

    if not project_id:
        logger.error("Ошибка: PROJECT_ID не найден в файле .env")
        return

    file_path = "questions.json"

    with open(file_path, "r", encoding="utf-8") as f:
        intents_data = json.load(f)

    for intent_name, data in intents_data.items():
        create_intent(
            project_id=project_id,
            display_name=intent_name,
            training_phrases_parts=data["questions"],
            message_texts=[data["answer"]],
        )


if __name__ == "__main__":
    main()
