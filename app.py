
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="🎯"
)

st.title("🎯 AI Interview Preparation Assistant")
st.write("Practice interviews with your personal AI interviewer.")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "review" not in st.session_state:
    st.session_state.review = None


# Sidebar settings
with st.sidebar:
    st.header("Interview Settings")

    role = st.selectbox(
        "Choose your role",
        ["Python Developer", "AI/ML Engineer", "Backend Developer"]
    )

    difficulty = st.selectbox(
        "Choose difficulty",
        ["Beginner", "Intermediate", "Advanced"]
    )

    if st.button("Start New Interview"):
        try:
            response = requests.post(
                f"{API_URL}/interview/start",
                json={
                    "role": role,
                    "difficulty": difficulty
                },
                timeout=120
            )

            response.raise_for_status()
            result = response.json()

            st.session_state.session_id = result["session_id"]

            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": result["message"]
                }
            ]

            st.session_state.interview_started = True
            st.session_state.review = None

            st.rerun()

        except requests.RequestException as error:
            st.error(f"Could not start interview: {error}")


# Display conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Chat input
if st.session_state.interview_started:

    answer = st.chat_input("Type your answer here...")

    if answer:
        st.session_state.messages.append({
            "role": "user",
            "content": answer
        })

        with st.chat_message("user"):
            st.write(answer)

        try:
            with st.spinner("Interviewer is thinking..."):
                response = requests.post(
                    f"{API_URL}/interview/respond",
                    json={
                        "session_id": st.session_state.session_id,
                        "answer": answer
                    },
                    timeout=120
                )

                response.raise_for_status()
                result = response.json()

            if "error" in result:
                st.error(result["error"])

            elif result.get("status") == "completed":

                st.session_state.interview_started = False
                st.session_state.review = result.get("review", {})

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result.get(
                        "message",
                        "Interview completed!"
                    )
                })

                st.rerun()

            else:
                next_message = result["message"]

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": next_message
                })

                st.rerun()

        except requests.RequestException as error:
            st.error(f"Could not send your answer: {error}")


# Display final interview report
if st.session_state.review:
    review = st.session_state.review

    st.divider()
    st.header("📊 Your Interview Report")

    st.metric(
        "Overall Score",
        f'{review.get("overall_score", 0)}/10'
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Technical Knowledge",
            f'{review.get("technical_knowledge", 0)}/10'
        )

    with col2:
        st.metric(
            "Communication",
            f'{review.get("communication", 0)}/10'
        )

    st.subheader("💪 Strengths")

    for item in review.get("strengths", []):
        st.write(f"• {item}")

    st.subheader("📚 Areas to Improve")

    for item in review.get("weak_areas", []):
        st.write(f"• {item}")

    st.subheader("🎯 Improvement Suggestions")

    for item in review.get("what_to_improve", []):
        st.write(f"• {item}")

    st.subheader("💬 Final Feedback")
    st.write(review.get("final_feedback", "No feedback available."))

