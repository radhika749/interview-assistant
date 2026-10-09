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
    ],
    "question_count": 1,
    "max_questions": 10,
    "completed": False
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
        return {"error": "Invalid session ID"}

    if session["completed"]:
        return {
            "status": "completed",
            "message": "This interview has already finished."
        }

    # Save candidate's answer
    session["conversation"].append({
        "speaker": "candidate",
        "message": data.answer
    })

    # Check whether the interview should finish
    if session["question_count"] >= session["max_questions"]:

        try:
            review = generate_final_review(
                session["role"],
                session["conversation"]
            )
        except Exception:
            session["conversation"].pop()
            return {
                "error": "Could not generate the final report. Please try again."
            }

        session["completed"] = True

        return {
            "status": "completed",
            "message": "Interview completed!",
            "review": review
        }

    # Generate the next question
    try:
        next_message = continue_interview(
            session["role"],
            session["difficulty"],
            session["conversation"]
        )
    except RuntimeError:
        session["conversation"].pop()
        return {
            "error": "AI is temporarily unavailable. Please try again."
        }

    # Save the next interviewer message
    session["conversation"].append({
        "speaker": "interviewer",
        "message": next_message
    })

    session["question_count"] += 1

    return {
        "status": "in_progress",
        "message": next_message,
        "question_number": session["question_count"]
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