import streamlit as st
import google.generativeai as genai
import json

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Mock Interview Agent")
st.title("🎤 Mock Interview Agent")

# -----------------------------
# API KEY
# -----------------------------
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    st.success("API Key Loaded")
except Exception as e:
    st.error("Missing GOOGLE_API_KEY in Streamlit Secrets")
    st.error(str(e))
    st.stop()

# -----------------------------
# MODEL (YOUR REQUESTED MODEL)
# -----------------------------
model = genai.GenerativeModel("gemini-2.5-flash-lite")

st.success("Gemini Model Initialized")

# -----------------------------
# SESSION STATE
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
# GENERATE QUESTION
# -----------------------------
def generate_question(topic, difficulty):

    prompt = f"""
You are an expert interviewer.

Topic: {topic}
Difficulty: {difficulty}

Generate ONLY ONE interview question.
Do NOT provide answer.
Return only the question.
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        st.error("QUESTION GENERATION ERROR")
        st.error(str(e))
        return "Unable to generate question."

# -----------------------------
# EVALUATE ANSWER (FIXED LOGIC)
# -----------------------------
def evaluate_answer(question, answer):

    prompt = f"""
You are an AI interviewer evaluator.

Question: {question}
Answer: {answer}

Return ONLY valid JSON:

{{
  "result": "Correct" or "Wrong",
  "correct_answer": "short answer"
}}
"""

    try:
        response = model.generate_content(prompt)

        data = json.loads(response.text)

        return data

    except Exception as e:
        st.error("EVALUATION ERROR")
        st.error(str(e))

        return {
            "result": "Wrong",
            "correct_answer": "Unable to evaluate"
        }

# -----------------------------
# START SCREEN
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
# INTERVIEW SCREEN
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

        st.write("Result:", result["result"])
        st.write("Correct Answer:", result["correct_answer"])

        # -----------------------------
        # FIXED SCORING LOGIC
        # -----------------------------
        if result["result"].lower() == "correct":
            st.session_state.score += 1

        # NEXT QUESTION
        if st.session_state.question_no < st.session_state.total_questions:

            st.session_state.question_no += 1

            st.session_state.current_question = generate_question(
                st.session_state.topic,
                st.session_state.difficulty
            )

            st.rerun()

        # FINAL RESULT
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
