import streamlit as st
import google.generativeai as genai

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Mock Interview Agent")

st.title("🎤 Mock Interview Agent")

# -----------------------------
# API Key
# -----------------------------
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    st.success("API Key Loaded")
except Exception as e:
    st.error("Missing GOOGLE_API_KEY in Streamlit Secrets")
    st.error(str(e))
    st.stop()

# -----------------------------
# IMPORTANT: Correct Model
# -----------------------------
model = genai.GenerativeModel("gemini-2.5-flash-lite")

st.success("Gemini Model Initialized")

# -----------------------------
# Session State
# -----------------------------
defaults = {
    "started": False,
    "score": 0,
    "question_no": 0,
    "current_question": "",
    "candidate_name": "",
    "topic": "",
    "difficulty": "",
    "total_questions": 5,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -----------------------------
# Generate Question
# -----------------------------
def generate_question(topic, difficulty):

    prompt = f"""
You are an expert interviewer.

Topic: {topic}
Difficulty: {difficulty}

Ask ONLY ONE interview question.
Do NOT provide answer.
Return only the question.
"""

    try:
        response = model.generate_content(prompt)

        # Debug (important for fixing)
        if hasattr(response, "text"):
            return response.text.strip()

        return "No response text received."

    except Exception as e:
        st.error("QUESTION GENERATION ERROR")
        st.error(type(e).__name__)
        st.error(str(e))
        return "Unable to generate question."

# -----------------------------
# Evaluate Answer
# -----------------------------
def evaluate_answer(question, answer):

    prompt = f"""
Question: {question}
Answer: {answer}

Evaluate correctness and give:
Result: Correct / Wrong
Correct Answer: <text>
"""

    try:
        response = model.generate_content(prompt)

        return response.text if hasattr(response, "text") else "No response"

    except Exception as e:
        return f"Evaluation error: {e}"

# -----------------------------
# Start Screen
# -----------------------------
if not st.session_state.started:

    name = st.text_input("Candidate Name")
    topic = st.text_input("Topic")

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"]
    )

    total_questions = st.number_input(
        "Number of Questions",
        1, 20, 5
    )

    if st.button("Start Interview"):

        if not name or not topic:
            st.warning("Fill all fields")
            st.stop()

        st.session_state.started = True
        st.session_state.candidate_name = name
        st.session_state.topic = topic
        st.session_state.difficulty = difficulty
        st.session_state.total_questions = total_questions
        st.session_state.question_no = 1
        st.session_state.score = 0

        st.session_state.current_question = generate_question(topic, difficulty)

        st.rerun()

# -----------------------------
# Interview Screen
# -----------------------------
else:

    st.subheader(
        f"Question {st.session_state.question_no} / {st.session_state.total_questions}"
    )

    st.write(st.session_state.current_question)

    answer = st.text_area("Your Answer")

    if st.button("Submit"):

        if not answer:
            st.warning("Enter answer first")
            st.stop()

        result = evaluate_answer(
            st.session_state.current_question,
            answer
        )

        st.write("### Evaluation")
        st.write(result)
        
        if result.strip().startswith("Result: Correct"):
            st.session_state.score += 1

        if st.session_state.question_no < st.session_state.total_questions:

            st.session_state.question_no += 1
            st.session_state.current_question = generate_question(
                st.session_state.topic,
                st.session_state.difficulty
            )

            st.rerun()

        else:

            st.success("Interview Completed")

            score = st.session_state.score
            total = st.session_state.total_questions

            st.write(f"Score: {score}/{total}")
            st.write(f"Percentage: {(score/total)*100:.2f}%")

            if st.button("Restart"):
                for k in defaults:
                    st.session_state[k] = defaults[k]
                st.rerun()
