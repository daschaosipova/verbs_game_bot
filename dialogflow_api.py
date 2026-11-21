from google.cloud import dialogflow_v2 as dialogflow


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
