from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

VALIDATION_PROMPT = """You are a classifier. Determine if the following question is related to football tactics, formations, playing styles, managers, or football history.

Respond with ONLY "yes" or "no".

Question: {question}"""

def is_football_tactics_question(question: str) -> bool:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": VALIDATION_PROMPT.format(question=question)}
        ],
        max_tokens=5,
        temperature=0
    )
    answer = response.choices[0].message.content.strip().lower()
    return answer == "yes"