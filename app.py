import streamlit as st
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AQ.Ab8RN6KkRNMrcDhw2xF_kOqYsOCYcLShS4FEKRkzJjJ_60uGcQ")

# Load Model
model = genai.GenerativeModel("gemini-3.1-flash-lite")

# Page Title
st.set_page_config(page_title="Mock Interview Agent")

st.title("🎤 Mock Interview ")

# Session State Initialization
if "started" not in st.session_state:
    st.session_state.started = False

if "score" not in st.session_state:
    st.session_state.score = 0

if "question_no" not in st.session_state:
    st.session_state.question_no = 0

if "current_question" not in st.session_state:
    st.session_state.current_question = ""

if "candidate_name" not in st.session_state:
    st.session_state.candidate_name = ""

if "topic" not in st.session_state:
    st.session_state.topic = ""

if "difficulty" not in st.session_state:
    st.session_state.difficulty = ""

if "total_questions" not in st.session_state:
    st.session_state.total_questions = 5


# Generate Question Function
def generate_question(topic, difficulty):

    prompt = f"""
    You are an expert technical interviewer.

    Topic: {topic}

    Difficulty Level: {difficulty}

    Rules:

    Easy:
    - Ask basic concepts and definitions.

    Medium:
    - Ask practical and application-oriented questions.

    Hard:
    - Ask advanced concepts, coding problems,
      optimization techniques, and real-world scenarios.

    Generate ONLY ONE interview question.

    Do not provide the answer.
    """

    response = model.generate_content(prompt)

    return response.text.strip()


# Start Screen
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


# Interview Screen
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

        eval_prompt = f"""
        Question:
        {st.session_state.current_question}

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

        evaluation = model.generate_content(eval_prompt)

        feedback = evaluation.text

        st.write("### Evaluation")
        st.write(feedback)

        if feedback.strip().startswith("Result: Correct"):
            st.session_state.score += 1

        # Next Question
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

        # Final Report
        else:

            st.success("✅ Interview Completed")

            score = st.session_state.score
            total = st.session_state.total_questions

            percentage = (score / total) * 100

            st.write("## Final Report")

            st.write(
                f"Candidate: "
                f"{st.session_state.candidate_name}"
            )

            st.write(
                f"Topic: "
                f"{st.session_state.topic}"
            )

            st.write(
                f"Difficulty: "
                f"{st.session_state.difficulty}"
            )

            st.write(
                f"Score: {score}/{total}"
            )

            st.write(
                f"Percentage: {percentage:.2f}%"
            )

            if percentage >= 80:
                performance = "Excellent"
            elif percentage >= 60:
                performance = "Good"
            elif percentage >= 40:
                performance = "Average"
            else:
                performance = "Needs Improvement"

            st.write(
                f"Performance: {performance}"
            )

            if st.button("Restart Interview"):

                st.session_state.started = False
                st.session_state.score = 0
                st.session_state.question_no = 0
                st.session_state.current_question = ""

                st.rerun()
