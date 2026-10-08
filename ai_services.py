import os
import json

from dotenv import load_dotenv
from google import genai


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ---------------- GENERATE QUESTION ----------------

def generate_question(topic: str, difficulty: str):

    prompt = f"""
    You are an interview preparation assistant.

    Generate ONE {difficulty} level interview question
    about {topic}.

    The question should be suitable for a job interview.

    Return only the interview question.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text


# ---------------- EVALUATE ANSWER ----------------

def evaluate_answer(topic: str, question: str, answer: str):

    prompt = f"""
    You are a friendly interview preparation teacher.

    The candidate is a beginner.

    Topic: {topic}

    Question: {question}

    Candidate Answer: {answer}

    Evaluate the answer.

    Return ONLY valid JSON in exactly this format:

    {{
        "score": 6,
        "correct": "What the candidate got right",
        "missing": "What the candidate missed",
        "explanation": "Simple explanation of what they need to learn",
        "improved_answer": "A short and easy interview answer",
        "memory_trick": "An easy way to remember it"
    }}

    Rules:
    - score must be a number from 0 to 10.
    - Use very simple English.
    - Keep explanations short.
    - Do not use Markdown.
    - Do not add anything before or after the JSON.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return json.loads(response.text)