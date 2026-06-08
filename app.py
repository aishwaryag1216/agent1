import streamlit as st
import google.generativeai as genai

# ----------------------------
# Configure Gemini API
# ----------------------------
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    st.error(
        "Google API key not found. "
        "Please add GOOGLE_API_KEY to Streamlit Secrets."
    )
    st.stop()

# ----------------------------
# Load Gemini Model
# ----------------------------
try:
    model = genai.GenerativeModel("gemini-2.5-flash")
except Exception as e:
    st.error(f"Model initialization error: {e}")
    st.stop()

# ----------------------------
# Page Configuration
# ----------------------------
st.set_page_config(page_title="Mock Interview Agent")

st.title("🎤 Mock Interview Agent")

# ----------------------------
# Session State Initialization
# ----------------------------
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

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ----------------------------
# Generate Question
# ----------------------------
def generate_question(topic, difficulty):
    prompt = f"""
    Topic: {topic}
    Difficulty: {difficulty}

    Generate one interview question only.
    """

    try:
        response = model.generate_content(prompt)
        st.write("DEBUG RESPONSE:", response)
        return response.text.strip()

    except Exception as e:
        st.error(f"FULL ERROR: {str(e)}")
        return "Unable to generate question."

# ----------------------------
# Evaluate Answer
# ----------------------------
def evaluate_answer(question, answer):

    prompt = f"""
Question:
{question}

Candidate Answer:
{answer}

Evaluate the answer.

Return EXACTLY in this format:

Result: Correct

Correct Answer:
<correct answer>

OR

Result: Wrong

Correct Answer:
<correct answer>
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Evaluation Error: {e}"

# ----------------------------
# Start Screen
# ----------------------------
if not st.session_state.started:

    candidate_name = st.text_input("Candidate Name")

    topic = st.text_input("Interview Topic")

    difficulty = st.selectbox(
        "Select Difficulty",
        ["Easy", "Medium", "Hard"]
    )

    total_questions = st.number_input(
        "Number of Questions",
        min_value=1,
        max_value=20,
        value=5
    )

    if st.button("Start Interview"):

        if not candidate_name.strip():
            st.warning("Please enter candidate name.")
            st.stop()

        if not topic.strip():
            st.warning("Please enter interview topic.")
            st.stop()

        st.session_state.started = True
        st.session_state.score = 0
        st.session_state.question_no = 1

        st.session_state.candidate_name = candidate_name
        st.session_state.topic = topic
        st.session_state.difficulty = difficulty
        st.session_state.total_questions = total_questions

        st.session_state.current_question = generate_question(
            topic,
            difficulty
        )

        st.rerun()

# ----------------------------
# Interview Screen
# ----------------------------
else:

    st.subheader(
        f"Question {st.session_state.question_no} / "
        f"{st.session_state.total_questions}"
    )

    st.write(st.session_state.current_question)

    answer = st.text_area(
        "Your Answer",
        key=f"answer_{st.session_state.question_no}"
    )

    if st.button("Submit Answer"):

        if not answer.strip():
            st.warning("Please enter your answer.")
            st.stop()

        feedback = evaluate_answer(
            st.session_state.current_question,
            answer
        )

        st.write("### Evaluation")
        st.write(feedback)

        if feedback.strip().startswith("Result: Correct"):
            st.session_state.score += 1

        if (
            st.session_state.question_no
            < st.session_state.total_questions
        ):

            st.session_state.question_no += 1

            st.session_state.current_question = generate_question(
                st.session_state.topic,
                st.session_state.difficulty
            )

            st.rerun()

        else:

            st.success("✅ Interview Completed")

            score = st.session_state.score
            total = st.session_state.total_questions

            percentage = (score / total) * 100

            st.write("## Final Report")
            st.write(f"Candidate: {st.session_state.candidate_name}")
            st.write(f"Topic: {st.session_state.topic}")
            st.write(f"Difficulty: {st.session_state.difficulty}")
            st.write(f"Score: {score}/{total}")
            st.write(f"Percentage: {percentage:.2f}%")

            if percentage >= 80:
                performance = "Excellent"
            elif percentage >= 60:
                performance = "Good"
            elif percentage >= 40:
                performance = "Average"
            else:
                performance = "Needs Improvement"

            st.write(f"Performance: {performance}")

            if st.button("Restart Interview"):

                for key, value in defaults.items():
                    st.session_state[key] = value

                st.rerun()
