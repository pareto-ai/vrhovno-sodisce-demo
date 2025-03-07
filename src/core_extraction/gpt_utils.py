
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)

def call_gpt_json(prompt: str, input_text: str, temperature=0.1) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=temperature,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": input_text},
        ],
        response_format={ "type": "json_object" }
    )
    return response.choices[0].message.content

def call_gpt(prompt: str, input_text: str, temperature=0.1) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=temperature,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": input_text},
        ],
    )
    return response.choices[0].message.content
