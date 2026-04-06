import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class Agent:
    def run(self, input_text: str) -> str:
        raise NotImplementedError


class ChatAgent(Agent):
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def run(self, input_text: str) -> str:
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful but safe AI assistant."},
                {"role": "user", "content": input_text}
            ]
        )
        return response.choices[0].message.content