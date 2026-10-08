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
            else:
                next_message = result["message"]

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": next_message
                })

                with st.chat_message("assistant"):
                    st.write(next_message)

        except requests.RequestException as error:
            st.error(f"Could not send your answer: {error}")