from fastapi import FastAPI
from pydantic import BaseModel
import uuid

from ai_services import (
    start_interview,
    continue_interview,
    generate_final_review
)


app = FastAPI()


# Temporary interview session storage
sessions = {}


@app.get("/")
def home():
    return {
        "message": "AI Interview Assistant is running"
    }


# ---------- START INTERVIEW ----------

class StartInterviewRequest(BaseModel):
    role: str
    difficulty: str


@app.post("/interview/start")
def start(data: StartInterviewRequest):

    session_id = str(uuid.uuid4())

    first_message = start_interview(
        data.role,
        data.difficulty
    )

    sessions[session_id] = {
        "role": data.role,
        "difficulty": data.difficulty,
        "conversation": [
            {
                "speaker": "interviewer",
                "message": first_message
            }
        ]
    }

    return {
        "session_id": session_id,
        "message": first_message
    }


# ---------- ANSWER INTERVIEW QUESTION ----------

class InterviewAnswerRequest(BaseModel):
    session_id: str
    answer: str


@app.post("/interview/respond")
def respond(data: InterviewAnswerRequest):

    session = sessions.get(data.session_id)

    if session is None:
        return {
            "error": "Invalid session ID"
        }

    # Save candidate's answer
    session["conversation"].append({
        "speaker": "candidate",
        "message": data.answer
    })

    # Ask AI what should come next
    next_message = continue_interview(
        session["role"],
        session["difficulty"],
        session["conversation"]
    )

    # Save AI response
    session["conversation"].append({
        "speaker": "interviewer",
        "message": next_message
    })

    return {
        "message": next_message
    }


# ---------- END INTERVIEW ----------

class EndInterviewRequest(BaseModel):
    session_id: str


@app.post("/interview/end")
def end_interview(data: EndInterviewRequest):

    session = sessions.get(data.session_id)

    if session is None:
        return {
            "error": "Invalid session ID"
        }

    review = generate_final_review(
        session["role"],
        session["conversation"]
    )

    return {
        "review": review
    }