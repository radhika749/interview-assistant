import os
import json
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# ---------- START INTERVIEW ----------

def start_interview(role: str, difficulty: str):

    prompt = f"""
    You are a professional but friendly technical interviewer.

    Start a realistic interview for a candidate applying for:
    Role: {role}

    Difficulty: {difficulty}

    Ask the first interview question.

    Rules:
    - Start with a simple introduction.
    - Ask only ONE question.
    - Do not give the answer.
    - Keep the question clear and natural.
    - Do not evaluate the candidate yet.

    Return only the message you would say to the candidate.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text


# ---------- CONTINUE INTERVIEW ----------

def continue_interview(
    role: str,
    difficulty: str,
    conversation: list
):
    prompt = f"""
    You are conducting a realistic technical interview.

    Candidate role: {role}
    Difficulty: {difficulty}

    Conversation so far:
    {json.dumps(conversation)}

    Continue the interview naturally.
    - Understand the candidate's latest answer.
    - Ask a relevant follow-up or a new question.
    - Ask only ONE question at a time.
    - Use simple, clear language.
    - Do not reveal the answer.
    - Do not give a score during the interview.

    Return only the next interviewer message.
    """

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=prompt
            )

            if response.text:
                return response.text

            return "I couldn't generate the next question. Please try again."

        except errors.APIError as error:
            print(f"Gemini API error: {error}")

            if attempt < 2:
                time.sleep(2 * (attempt + 1))

    raise RuntimeError(
        "Gemini is temporarily unavailable. Please try again later."
    )


# ---------- FINAL INTERVIEW REVIEW ----------

def generate_final_review(
    role: str,
    conversation: list
):

    prompt = f"""
    You are an interview evaluator.

    Candidate role:
    {role}

    Complete interview conversation:
    {json.dumps(conversation)}

    Give the candidate a final interview review.

    Return ONLY valid JSON in exactly this format:

    {{
        "overall_score": 7,
        "technical_knowledge": 7,
        "communication": 7,
        "strengths": [
            "strength 1",
            "strength 2"
        ],
        "weak_areas": [
            "weak area 1",
            "weak area 2"
        ],
        "what_to_improve": [
            "improvement 1",
            "improvement 2"
        ],
        "final_feedback": "Short and simple overall feedback"
    }}

    Rules:
    - Scores must be numbers from 0 to 10.
    - Use simple English.
    - Be honest but encouraging.
    - Focus on the actual answers given by the candidate.
    - Do not invent information.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return json.loads(response.text)