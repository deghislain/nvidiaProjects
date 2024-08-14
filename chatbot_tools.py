from crewai_tools import BaseTool
import requests

login_microservice_url = "http://127.0.0.1:8080/login"


class CustomLoginTool(BaseTool):
    name: str = "Authenticator"
    description: str = "Use when you have an username"

    def _run(self, username: str, password: str) -> str:
        global response
        if username is not None:
            response = requests.get(login_microservice_url, json={'username': f"""{username}""", 'password': 'armelo'})

        return response.content
