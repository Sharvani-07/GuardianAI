from flask import Blueprint, render_template, request, redirect, url_for, session

learning_bp = Blueprint("learning", __name__, url_prefix="/learning")


# ---------------------------------------------------------
# Sample learning questions
# ---------------------------------------------------------

QUESTIONS = {
    "Python": [
        {
            "question": "What is a variable in Python?",
            "answer": "A variable is a name used to store a value in Python."
        },
        {
            "question": "What is a loop?",
            "answer": "A loop is used to repeatedly execute a block of code."
        },
        {
            "question": "What is a function?",
            "answer": "A function is a reusable block of code that performs a specific task."
        }
    ],

    "SQL": [
        {
            "question": "What is SQL?",
            "answer": "SQL is a language used to communicate with and manage relational databases."
        },
        {
            "question": "What is a primary key?",
            "answer": "A primary key uniquely identifies each record in a database table."
        },
        {
            "question": "What is the purpose of SELECT?",
            "answer": "SELECT is used to retrieve data from a database."
        }
    ],

    "Java": [
        {
            "question": "What is a class in Java?",
            "answer": "A class is a blueprint for creating objects in Java."
        },
        {
            "question": "What is inheritance?",
            "answer": "Inheritance allows one class to acquire properties and methods of another class."
        },
        {
            "question": "What is an object?",
            "answer": "An object is an instance of a class."
        }
    ]
}


# ---------------------------------------------------------
# Learning home
# ---------------------------------------------------------

@learning_bp.route("/")
def learning_home():

    subjects = list(QUESTIONS.keys())

    return render_template(
        "learning.html",
        subjects=subjects
    )


# ---------------------------------------------------------
# Start learning
# ---------------------------------------------------------

@learning_bp.route("/start", methods=["POST"])
def start_learning():

    subject = request.form.get("subject")

    if subject not in QUESTIONS:
        return redirect(url_for("learning.learning_home"))

    session["learning_subject"] = subject
    session["learning_index"] = 0

    return redirect(url_for("learning.question"))


# ---------------------------------------------------------
# Display question
# ---------------------------------------------------------

@learning_bp.route("/question")
def question():

    subject = session.get("learning_subject")

    if not subject:
        return redirect(url_for("learning.learning_home"))

    index = session.get("learning_index", 0)

    questions = QUESTIONS[subject]

    if index >= len(questions):
        return redirect(url_for("learning.progress"))

    current_question = questions[index]

    return render_template(
        "learning_question.html",
        subject=subject,
        question=current_question["question"],
        question_number=index + 1,
        total_questions=len(questions)
    )


# ---------------------------------------------------------
# Evaluate answer
# ---------------------------------------------------------

@learning_bp.route("/submit", methods=["POST"])
def submit_answer():

    subject = session.get("learning_subject")

    if not subject:
        return redirect(url_for("learning.learning_home"))

    index = session.get("learning_index", 0)

    questions = QUESTIONS[subject]

    user_answer = request.form.get("answer", "").strip()

    correct_answer = questions[index]["answer"]

    # Simple keyword-based evaluation
    correct_words = set(
        correct_answer.lower().replace(".", "").split()
    )

    user_words = set(
        user_answer.lower().replace(".", "").split()
    )

    if len(user_words) == 0:
        score = 0
    else:
        matched = correct_words.intersection(user_words)
        score = int((len(matched) / len(correct_words)) * 100)

    if score >= 70:
        feedback = "Good answer! You understood the main concept."
    elif score >= 40:
        feedback = "Partially correct. Review the concept and try again."
    else:
        feedback = "Your answer needs improvement. Review the explanation."

    session["last_score"] = score
    session["last_feedback"] = feedback
    session["last_correct_answer"] = correct_answer

    return render_template(
        "learning_result.html",
        score=score,
        feedback=feedback,
        correct_answer=correct_answer
    )


# ---------------------------------------------------------
# Next question
# ---------------------------------------------------------

@learning_bp.route("/next")
def next_question():

    index = session.get("learning_index", 0)

    session["learning_index"] = index + 1

    return redirect(url_for("learning.question"))


# ---------------------------------------------------------
# Progress
# ---------------------------------------------------------

@learning_bp.route("/progress")
def progress():

    subject = session.get("learning_subject", "Learning")

    return render_template(
        "learning_progress.html",
        subject=subject
    )