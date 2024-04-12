import requests

from dotenv import load_dotenv
from os import environ

load_dotenv()

YANDEX_API_TOKEN = environ.get("yandex_api_token")
YANDEX_FOLDER_ID = environ.get("yandex_folder_id")

BASE_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"


class YaGPT:
    def __init__(self, folder_id: str, token: str) -> None:
        self.folder_id = folder_id
        self.token = token

    def ask(self, *messages: dict) -> None | str:
        """``` 
            ask([
                {
                    "role": "system",
                    "text": "Напиши 8-10 вопросов по которым пользователь должен будет ответить чтобы придумать эпитафию и биографию!"
                },
                {
                    "role": "user",
                    "text": "Вид текста: эпитафия. Тема: качества и характер, но при этом краткие и понятные вопросы на 1-2 предложения."
                }
            ])
            ```"""
        data = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0,
                "maxTokens": "2000"
            },
            "messages": messages
        }
        try:
            res = requests.post(
                BASE_URL,
                json=data,
                headers={"Authorization": f"Api-Key {self.token}"}
            )
            res.raise_for_status()
            return res.json()['result']['alternatives'][0]['message']['text']
        except (KeyError, IndexError):
            return


if __name__ == "__main__":
    yg = YaGPT(YANDEX_FOLDER_ID, YANDEX_API_TOKEN)
    res = yg.ask(
        {
            "role": "system",
            "text": "Напиши 8-10 вопросов по которым пользователь должен будет ответить чтобы придумать эпитафию и биографию!"
        },
        {
            "role": "user",
            "text": "Вид текста: эпитафия. Тема: качества и характер, но при этом краткие и понятные вопросы на 1-2 предложения."
        }
    )
    print(res)
