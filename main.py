from fastapi import FastAPI
from pydantic import BaseModel
import uuid

from ai_services import generate_question, evaluate_answer


app = FastAPI()


# Temporary storage
sessions = {}


@app.get("/")
def home():
    return {
        "message": "Interview Assistant API is running"
    }


# ---------- START INTERVIEW ----------

class InterviewStartRequest(BaseModel):
    topic: str
    difficulty: str


@app.post("/interview/start")
def start_interview(data: InterviewStartRequest):

    session_id = str(uuid.uuid4())

    question = generate_question(
        data.topic,
        data.difficulty
    )

    sessions[session_id] = {
        "topic": data.topic,
        "difficulty": data.difficulty,
        "question": question
    }

    return {
        "session_id": session_id,
        "topic": data.topic,
        "difficulty": data.difficulty,
        "question": question
    }


# ---------- SUBMIT ANSWER ----------

class AnswerRequest(BaseModel):
    session_id: str
    answer: str


@app.post("/interview/answer")
def submit_answer(data: AnswerRequest):

    session = sessions.get(data.session_id)

    if session is None:
        return {
            "error": "Invalid session ID"
        }

    evaluation = evaluate_answer(
        session["topic"],
        session["question"],
        data.answer
    )

    return {
        "question": session["question"],
        "answer": data.answer,
        "evaluation": evaluation
    }