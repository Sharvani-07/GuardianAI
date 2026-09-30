import os
import random
import sqlite3
import tempfile

from flask import Flask, render_template, request, redirect, jsonify
from werkzeug.utils import secure_filename

from services.handwritten_evaluator import evaluate_answer
from services.document_evaluator import evaluate_document

from question_bank import get_questions

# ---------------------------------------------------------
# QUESTION BANK COMPATIBILITY
# ---------------------------------------------------------
# Supports either QUESTION_BANK or QUESTIONS in
# question_bank.py

try:
    from question_bank import QUESTION_BANK
except ImportError:
    from question_bank import QUESTIONS as QUESTION_BANK


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = "guardianai-secret-key"

DATABASE = "guardianai.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_database():

    connection = get_connection()

    cursor = connection.cursor()

    # -----------------------------------------------------
    # AGENTS
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'Active',
            risk TEXT DEFAULT 'Low'
        )
    """)

    # -----------------------------------------------------
    # AUDIT LOGS
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT,
            action TEXT,
            risk TEXT,
            score INTEGER,
            decision TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # APPROVAL REQUESTS
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS approval_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT,
            action TEXT,
            risk TEXT,
            score INTEGER,
            status TEXT DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # STUDENTS
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT
        )
    """)

    # -----------------------------------------------------
    # LEARNING PERFORMANCE
    # -----------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            topic TEXT,
            score REAL,
            assessment_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()

    connection.close()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    return render_template("index.html")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    connection = get_connection()

    cursor = connection.cursor()

    # -----------------------------------------------------
    # GET AGENTS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT *
        FROM agents
        ORDER BY id DESC
    """)

    agents_list = cursor.fetchall()

    # -----------------------------------------------------
    # GET APPROVAL REQUESTS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT *
        FROM approval_requests
        ORDER BY id DESC
    """)

    approvals = cursor.fetchall()

    # -----------------------------------------------------
    # GET STUDENTS
    # -----------------------------------------------------

    cursor.execute("""
        SELECT *
        FROM students
        ORDER BY name
    """)

    students = cursor.fetchall()

    connection.close()

    # -----------------------------------------------------
    # SEND DATA TO DASHBOARD
    # -----------------------------------------------------

    return render_template(
        "dashboard.html",
        agents=agents_list,
        approvals=approvals,
        students=students
    )


# =========================================================
# AGENTS
# =========================================================

@app.route("/agents")
def agents():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM agents
        ORDER BY id DESC
    """)

    agents_list = cursor.fetchall()

    connection.close()

    return render_template(
        "agents.html",
        agents=agents_list
    )


# =========================================================
# ADD AGENT
# =========================================================

@app.route("/add_agent", methods=["GET", "POST"])
def add_agent():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        status = request.form.get(
            "status",
            "Active"
        )

        risk = request.form.get(
            "risk",
            "Low"
        )

        if name:

            connection = get_connection()

            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO agents
                (name, status, risk)
                VALUES (?, ?, ?)
            """, (
                name,
                status,
                risk
            ))

            connection.commit()

            connection.close()

        return redirect("/agents")

    return render_template("add_agent.html")


# =========================================================
# DELETE AGENT
# =========================================================

@app.route("/delete_agent/<int:agent_id>")
def delete_agent(agent_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM agents
        WHERE id = ?
    """, (
        agent_id,
    ))

    connection.commit()

    connection.close()

    return redirect("/agents")


# =========================================================
# RISK MANAGEMENT
# =========================================================
@app.route("/risk", methods=["GET", "POST"])
def risk():

    risk = None
    score = None
    decision = None
    selected_agent = None
    selected_action = None

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, name, status, risk
        FROM agents
        ORDER BY id DESC
    """)

    agents = cursor.fetchall()

    connection.close()

    # -------------------------------------------------
    # DEMO AGENTS
    # -------------------------------------------------

    if not agents:

        agents = [
            {
                "id": 1,
                "name": "GuardianAI Evaluation Agent",
                "status": "Active",
                "risk": "Low"
            },
            {
                "id": 2,
                "name": "Learning Evaluation Agent",
                "status": "Active",
                "risk": "Medium"
            },
            {
                "id": 3,
                "name": "File Management Agent",
                "status": "Active",
                "risk": "High"
            }
        ]

    # -------------------------------------------------
    # RISK EVALUATION
    # -------------------------------------------------

    if request.method == "POST":

        selected_agent = request.form.get("agent")
        selected_action = request.form.get("action")

        # LOW RISK
        if selected_action in [
            "Read Email",
            "Generate Report"
        ]:

            risk = "Low"
            score = 20
            decision = "ALLOW"

        # MEDIUM RISK
        elif selected_action in [
            "Modify Settings",
            "Access Customer Data"
        ]:

            risk = "Medium"
            score = 60
            decision = "APPROVAL"

        # HIGH RISK
        elif selected_action in [
            "Delete Files",
            "Delete Database",
            "Change Permissions"
        ]:

            risk = "High"
            score = 95
            decision = "BLOCK"

        # -------------------------------------------------
        # SAVE AUDIT LOG
        # -------------------------------------------------

        if risk is not None:

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO audit_logs
                (
                    agent,
                    action,
                    risk,
                    score,
                    decision
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                selected_agent,
                selected_action,
                risk,
                score,
                decision
            ))

            # -------------------------------------------------
            # CREATE APPROVAL REQUEST
            # -------------------------------------------------

            if decision == "APPROVAL":

                cursor.execute("""
                    INSERT INTO approval_requests
                    (
                        agent,
                        action,
                        risk,
                        score,
                        status
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    selected_agent,
                    selected_action,
                    risk,
                    score,
                    "PENDING"
                ))

            connection.commit()
            connection.close()

    return render_template(
        "risk.html",
        agents=agents,
        risk=risk,
        score=score,
        decision=decision,
        selected_agent=selected_agent,
        selected_action=selected_action
    )


# =========================================================
# APPROVAL REQUESTS
# =========================================================
@app.route("/approval")
def approval():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            agent,
            action,
            risk,
            score,
            status
        FROM approval_requests
        ORDER BY id DESC
    """)

    requests = cursor.fetchall()

    connection.close()

    return render_template(
        "approval.html",
        requests=requests
    )
# =========================================================
# APPROVE REQUEST
# =========================================================

@app.route("/approve/<int:request_id>")
def approve(request_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE approval_requests
        SET status = 'APPROVED'
        WHERE id = ?
    """, (
        request_id,
    ))

    connection.commit()

    connection.close()

    return redirect("/approval")


# =========================================================
# REJECT REQUEST
# =========================================================

@app.route("/reject/<int:request_id>")
def reject(request_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE approval_requests
        SET status = 'REJECTED'
        WHERE id = ?
    """, (
        request_id,
    ))

    connection.commit()

    connection.close()

    return redirect("/approval")


# =========================================================
# AUDIT LOGS
# =========================================================

@app.route("/audit_logs")
def audit_logs():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM audit_logs
        ORDER BY id DESC
    """)

    logs = cursor.fetchall()

    connection.close()

    return render_template(
        "audit_logs.html",
        logs=logs
    )


# =========================================================
# POLICIES
# =========================================================

@app.route("/policies")
def policies():

    return render_template("policies.html")


# =========================================================
# ANALYTICS
# =========================================================

@app.route("/analytics")
def analytics():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM audit_logs
    """)

    total_actions = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM audit_logs
        WHERE decision = 'ALLOW'
    """)

    allowed = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM audit_logs
        WHERE decision = 'HUMAN APPROVAL'
    """)

    approval_count = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM audit_logs
        WHERE decision = 'BLOCK'
    """)

    blocked = cursor.fetchone()["total"]

    connection.close()

    return render_template(
        "analytics.html",
        total_actions=total_actions,
        allowed=allowed,
        approval_count=approval_count,
        blocked=blocked
    )


# =========================================================
# LEARNING DASHBOARD
# =========================================================
@app.route("/learning")
def learning():

    student_id = request.args.get("student_id", type=int)

    connection = get_connection()
    cursor = connection.cursor()

    # Get all students
    cursor.execute("""
        SELECT *
        FROM students
        ORDER BY name
    """)

    students = cursor.fetchall()

    selected_student = None
    performance = []

    overall_score = 0

    topic_analysis = []
    recommendations = []

    practice_topics = []

    overall_recommendation = ""

    # Check whether a student was selected
    if student_id:

        cursor.execute("""
            SELECT *
            FROM students
            WHERE id = ?
        """, (student_id,))

        selected_student = cursor.fetchone()

        if selected_student:

            # Get student's assessment history
            cursor.execute("""
                SELECT *
                FROM learning_performance
                WHERE student_id = ?
                ORDER BY created_at DESC, id DESC
            """, (student_id,))

            performance = cursor.fetchall()

            # Calculate overall score
            if performance:

                scores = []

                for result in performance:

                    try:
                        scores.append(float(result["score"]))
                    except:
                        pass

                if scores:

                    overall_score = round(
                        sum(scores) / len(scores),
                        1
                    )

            # Get topic-wise performance
            cursor.execute("""
                SELECT
                    topic,
                    AVG(score) AS average_score,
                    COUNT(*) AS attempts
                FROM learning_performance
                WHERE student_id = ?
                GROUP BY topic
                ORDER BY average_score ASC
            """, (student_id,))

            topic_rows = cursor.fetchall()

            for row in topic_rows:

                topic_average = float(
                    row["average_score"] or 0
                )

                attempts = int(
                    row["attempts"] or 0
                )

                topic_name = row["topic"] or "General"

                topic_analysis.append({
                    "topic": topic_name,
                    "average_score": round(
                        topic_average,
                        1
                    ),
                    "attempts": attempts
                })

                # Priority learning
                if topic_average < 60:

                    practice_topics.append(
                        topic_name
                    )

                    recommendations.append({
                        "topic": topic_name,
                        "type": "priority",
                        "message": (
                            "This topic needs priority "
                            "learning. Review the fundamentals "
                            "and complete additional practice."
                        )
                    })

                # Needs practice
                elif topic_average < 80:

                    practice_topics.append(
                        topic_name
                    )

                    recommendations.append({
                        "topic": topic_name,
                        "type": "practice",
                        "message": (
                            "You are making good progress. "
                            "Practice this topic further before "
                            "moving to advanced concepts."
                        )
                    })

                # Strong topic
                else:

                    recommendations.append({
                        "topic": topic_name,
                        "type": "strong",
                        "message": (
                            "Strong performance. Try advanced "
                            "questions and challenging concepts."
                        )
                    })

            # Overall recommendation
            if overall_score < 60:

                overall_recommendation = (
                    "GuardianAI recommends focusing on "
                    "fundamental concepts and completing "
                    "additional practice assessments."
                )

            elif overall_score < 80:

                overall_recommendation = (
                    "You are making good progress. GuardianAI "
                    "recommends additional practice in topics "
                    "where your performance is between 60% "
                    "and 79%."
                )

            else:

                overall_recommendation = (
                    "Excellent performance. GuardianAI "
                    "recommends advanced questions and "
                    "challenging concepts."
                )

    connection.close()

    return render_template(
        "learning.html",
        students=students,
        selected_student=selected_student,
        performance=performance,
        overall_score=overall_score,
        topic_analysis=topic_analysis,
        recommendations=recommendations,
        practice_topics=practice_topics,
        overall_recommendation=overall_recommendation
    ) 
# =========================================================
# ADD STUDENT
# =========================================================

@app.route(
    "/learning/add_student",
    methods=["GET", "POST"]
)
def add_student():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        if name:

            connection = get_connection()

            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO students
                (
                    name,
                    email
                )
                VALUES (?, ?)
            """, (
                name,
                email
            ))

            connection.commit()

            connection.close()

        return redirect("/learning")

    return render_template(
        "add_student.html"
    )


# =========================================================
# ADD PERFORMANCE
# =========================================================

@app.route(
    "/learning/add_performance",
    methods=["GET", "POST"]
)
def add_performance():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM students
        ORDER BY name
    """)

    students = cursor.fetchall()

    if request.method == "POST":

        student_id = request.form.get(
            "student_id",
            type=int
        )

        topic = request.form.get(
            "topic",
            ""
        ).strip()

        score = request.form.get(
            "score",
            type=float
        )

        assessment_name = request.form.get(
            "assessment_name",
            "Manual Assessment"
        )

        if student_id and topic and score is not None:

            cursor.execute("""
                INSERT INTO learning_performance
                (
                    student_id,
                    topic,
                    score,
                    assessment_name
                )
                VALUES (?, ?, ?, ?)
            """, (
                student_id,
                topic,
                score,
                assessment_name
            ))

            connection.commit()

        connection.close()

        return redirect("/learning")

    connection.close()

    return render_template(
        "add_performance.html",
        students=students
    )


# =========================================================
# ADAPTIVE QUESTION GENERATOR
# =========================================================

@app.route("/learning/questions")
def learning_questions():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM students
        ORDER BY name ASC
    """)

    students = cursor.fetchall()

    student_id = request.args.get(
        "student_id",
        type=int
    )

    selected_student = None

    if student_id:

        cursor.execute("""
            SELECT *
            FROM students
            WHERE id = ?
        """, (
            student_id,
        ))

        selected_student = cursor.fetchone()

    topic = request.args.get(
        "topic"
    )

    level = request.args.get(
        "level"
    )

    questions = []

    # -----------------------------------------------------
    # GENERATE QUESTIONS
    # -----------------------------------------------------

    if student_id and topic:

        cursor.execute("""
            SELECT AVG(score) AS average_score
            FROM learning_performance
            WHERE student_id = ?
            AND topic = ?
        """, (
            student_id,
            topic
        ))

        result = cursor.fetchone()

        # -------------------------------------------------
        # AUTOMATIC DIFFICULTY
        # -------------------------------------------------

        if result and result["average_score"] is not None:

            average_score = float(
                result["average_score"]
            )

            if average_score < 40:

                level = "Beginner"

            elif average_score < 80:

                level = "Intermediate"

            else:

                level = "Advanced"

        else:

            level = "Beginner"

        questions = get_questions(
            topic,
            level
        )

        # -------------------------------------------------
        # IMPORTANT:
        #
        # DO NOT SHUFFLE QUESTIONS HERE.
        #
        # The submit route gets the questions again.
        # Keeping the same order prevents question_0,
        # question_1 etc. from being matched incorrectly.
        # -------------------------------------------------

        questions = questions.copy()

    connection.close()

    # -----------------------------------------------------
    # DYNAMIC TOPICS
    # -----------------------------------------------------

    topics = list(
        QUESTION_BANK.keys()
    )

    # -----------------------------------------------------
    # RENDER PAGE
    # -----------------------------------------------------

    return render_template(
        "questions.html",
        students=students,
        selected_student=selected_student,
        topic=topic,
        level=level,
        questions=questions,
        topics=topics
    )


# =========================================================
# SUBMIT ADAPTIVE QUIZ
# =========================================================

@app.route(
    "/learning/questions/submit",
    methods=["POST"]
)
def submit_learning_questions():

    # -----------------------------------------------------
    # READ FORM DATA
    # -----------------------------------------------------

    student_id = request.form.get(
        "student_id",
        type=int
    )

    topic = request.form.get(
        "topic",
        ""
    ).strip()

    level = request.form.get(
        "level",
        "Beginner"
    ).strip()

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not student_id:

        return (
            "Student ID is missing.",
            400
        )

    if not topic:

        return (
            "Topic is missing.",
            400
        )

    # -----------------------------------------------------
    # GET SAME QUESTION ORDER
    # -----------------------------------------------------

    questions = get_questions(
        topic,
        level
    )

    # -----------------------------------------------------
    # EVALUATE
    # -----------------------------------------------------

    correct = 0

    answered = 0

    for index, question in enumerate(questions):

        user_answer = request.form.get(
            f"question_{index}"
        )

        if user_answer:

            answered += 1

        if user_answer == question["answer"]:

            correct += 1

    # -----------------------------------------------------
    # SCORE
    # -----------------------------------------------------

    total = len(questions)

    if total > 0:

        score = round(
            (correct / total) * 100,
            1
        )

    else:

        score = 0

    # -----------------------------------------------------
    # SAVE PERFORMANCE
    # -----------------------------------------------------

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO learning_performance
        (
            student_id,
            topic,
            score,
            assessment_name
        )
        VALUES (?, ?, ?, ?)
    """, (
        student_id,
        topic,
        score,
        "Adaptive Quiz"
    ))

    connection.commit()

    connection.close()

    # -----------------------------------------------------
    # RESULT PAGE
    # -----------------------------------------------------

    return render_template(
        "quiz_result.html",
        student_id=student_id,
        topic=topic,
        level=level,
        correct=correct,
        total=total,
        answered=answered,
        score=score
    )
# =========================================================
# LEARNING PROGRESS
# =========================================================
@app.route("/learning/progress")
def learning_progress():

    student_id = request.args.get(
        "student_id",
        type=int
    )

    connection = get_connection()
    cursor = connection.cursor()

    # -------------------------------------------------
    # GET ALL STUDENTS
    # -------------------------------------------------

    cursor.execute("""
        SELECT *
        FROM students
        ORDER BY name
    """)

    students = cursor.fetchall()

    # -------------------------------------------------
    # DEFAULT VALUES
    # -------------------------------------------------

    performance = []
    topic_performance = []
    selected_student = None

    average_score = 0
    latest_score = 0
    previous_score = 0
    improvement = 0

    total_assessments = 0

    strong_topics = 0
    practice_topics = 0
    priority_topics = 0

    # -------------------------------------------------
    # SELECTED STUDENT
    # -------------------------------------------------

    if student_id:

        cursor.execute("""
            SELECT *
            FROM students
            WHERE id = ?
        """, (student_id,))

        selected_student = cursor.fetchone()

        # -------------------------------------------------
        # ASSESSMENT HISTORY
        # -------------------------------------------------

        cursor.execute("""
            SELECT *
            FROM learning_performance
            WHERE student_id = ?
            ORDER BY created_at DESC, id DESC
        """, (student_id,))

        performance = cursor.fetchall()

        total_assessments = len(performance)

        # -------------------------------------------------
        # OVERALL SCORE
        # -------------------------------------------------

        if performance:

            scores = []

            for item in performance:

                try:
                    scores.append(
                        float(item["score"])
                    )
                except:
                    pass

            if scores:

                average_score = round(
                    sum(scores) / len(scores),
                    1
                )

                latest_score = round(
                    scores[0],
                    1
                )

                if len(scores) >= 2:

                    previous_score = round(
                        scores[1],
                        1
                    )

                    improvement = round(
                        latest_score - previous_score,
                        1
                    )

        # -------------------------------------------------
        # TOPIC-WISE PERFORMANCE
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                topic,
                AVG(score) AS average_score,
                COUNT(*) AS attempts
            FROM learning_performance
            WHERE student_id = ?
            GROUP BY topic
            ORDER BY average_score ASC
        """, (student_id,))

        topic_rows = cursor.fetchall()

        for row in topic_rows:

            topic_average = float(
                row["average_score"] or 0
            )

            attempts = int(
                row["attempts"] or 0
            )

            if topic_average >= 80:

                status = "Strong"
                status_class = "strong"

                strong_topics += 1

            elif topic_average >= 60:

                status = "Needs Practice"
                status_class = "practice"

                practice_topics += 1

            else:

                status = "Priority Learning"
                status_class = "priority"

                priority_topics += 1

            topic_performance.append({
                "topic": row["topic"] or "General",
                "average_score": round(
                    topic_average,
                    1
                ),
                "attempts": attempts,
                "status": status,
                "status_class": status_class
            })

    connection.close()

    # -------------------------------------------------
    # PERSONALIZED RECOMMENDATION
    # -------------------------------------------------

    recommendation = ""

    if selected_student:

        if priority_topics > 0:

            recommendation = (
                "GuardianAI identified topic areas that need "
                "priority learning. Review the fundamentals "
                "and complete additional practice assessments."
            )

        elif practice_topics > 0:

            recommendation = (
                "You are making good progress. GuardianAI "
                "recommends additional practice in the topics "
                "that are currently between 60% and 79%."
            )

        elif strong_topics > 0:

            recommendation = (
                "Excellent progress. GuardianAI recommends "
                "trying advanced questions and challenging "
                "concepts to continue improving."
            )

        else:

            recommendation = (
                "Complete more assessments to generate "
                "personalized learning recommendations."
            )

    return render_template(
        "progress.html",

        students=students,

        selected_student=selected_student,

        performance=performance,

        topic_performance=topic_performance,

        average_score=average_score,

        latest_score=latest_score,

        previous_score=previous_score,

        improvement=improvement,

        total_assessments=total_assessments,

        strong_topics=strong_topics,

        practice_topics=practice_topics,

        priority_topics=priority_topics,

        recommendation=recommendation
    )
# =========================================================
# VOICE ANSWER EVALUATION
# =========================================================

@app.route("/voice", methods=["GET", "POST"])
def voice():

    if request.method == "POST":

        # -------------------------------------------------
        # GET FORM DATA
        # -------------------------------------------------

        student_name = request.form.get(
            "student_name",
            ""
        ).strip()

        question = request.form.get(
            "question",
            ""
        ).strip()

        expected_answer = request.form.get(
            "expected_answer",
            ""
        ).strip()

        keywords_text = request.form.get(
            "keywords",
            ""
        ).strip()

        recognized_answer = request.form.get(
            "recognized_answer",
            ""
        ).strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not student_name:

            return jsonify({
                "success": False,
                "message": "Please enter student name."
            })

        if not recognized_answer:

            return jsonify({
                "success": False,
                "message": "No recognised answer was provided."
            })

        # -------------------------------------------------
        # CONVERT KEYWORDS
        # -------------------------------------------------

        keywords = [
            item.strip()
            for item in keywords_text.split(",")
            if item.strip()
        ]

        # -------------------------------------------------
        # EVALUATE ANSWER
        # -------------------------------------------------

        result = evaluate_answer(
            recognized_answer,
            expected_answer,
            keywords
        )

        # -------------------------------------------------
        # GET SCORE
        # -------------------------------------------------

        raw_score = result.get(
            "score",
            0
        )

        try:

            score = float(raw_score)

        except:

            score = 0

        # If evaluator returns score out of 10,
        # convert it into percentage.

        if score <= 10:

            score = score * 10

        score = round(
            score,
            1
        )

        # Keep score within 0-100.

        if score < 0:
            score = 0

        if score > 100:
            score = 100

        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        connection = get_connection()

        cursor = connection.cursor()

        # -------------------------------------------------
        # FIND STUDENT
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT *
            FROM students
            WHERE LOWER(name) = LOWER(?)
            """,
            (
                student_name,
            )
        )

        student = cursor.fetchone()

        # -------------------------------------------------
        # CREATE STUDENT IF NOT FOUND
        # -------------------------------------------------

        if not student:

            cursor.execute(
                """
                INSERT INTO students
                (
                    name,
                    email
                )
                VALUES
                (
                    ?,
                    ?
                )
                """,
                (
                    student_name,
                    ""
                )
            )

            student_id = cursor.lastrowid

        else:

            student_id = student["id"]

        # -------------------------------------------------
        # TOPIC
        # -------------------------------------------------

        topic = question

        if not topic:

            topic = "Voice Assessment"

        # -------------------------------------------------
        # SAVE PERFORMANCE
        # -------------------------------------------------

        cursor.execute(
            """
            INSERT INTO learning_performance
            (
                student_id,
                topic,
                score,
                assessment_name,
                created_at
            )
            VALUES
            (
                ?,
                ?,
                ?,
                ?,
                datetime('now')
            )
            """,
            (
                student_id,
                topic,
                score,
                "Voice Answer Evaluation"
            )
        )

        connection.commit()

        # -------------------------------------------------
        # GET TOPIC AVERAGE
        # -------------------------------------------------

        cursor.execute(
            """
            SELECT
                AVG(score) AS average_score,
                COUNT(*) AS attempts
            FROM learning_performance
            WHERE student_id = ?
            AND topic = ?
            """,
            (
                student_id,
                topic
            )
        )

        topic_data = cursor.fetchone()

        connection.close()

        # -------------------------------------------------
        # TOPIC ANALYSIS
        # -------------------------------------------------

        topic_average = 0
        attempts = 0

        if topic_data:

            topic_average = float(
                topic_data["average_score"] or 0
            )

            attempts = int(
                topic_data["attempts"] or 0
            )

        # -------------------------------------------------
        # PERSONALIZED RECOMMENDATION
        # -------------------------------------------------

        if topic_average >= 80:

            learning_status = "Strong"

            learning_level = "Advanced"

            recommendation = (
                "Excellent performance. "
                "Continue with advanced questions "
                "and challenging concepts."
            )

        elif topic_average >= 60:

            learning_status = "Needs Practice"

            learning_level = "Intermediate"

            recommendation = (
                "Good progress. Practice this topic "
                "with additional questions before "
                "moving to advanced concepts."
            )

        else:

            learning_status = "Priority Learning"

            learning_level = "Beginner"

            recommendation = (
                "This topic needs more attention. "
                "Review the fundamental concepts "
                "and attempt more practice questions."
            )

        # -------------------------------------------------
        # RETURN RESULT
        # -------------------------------------------------

        return jsonify({

            "success": True,

            "student_name": student_name,

            "student_id": student_id,

            "question": question,

            "recognized_answer": recognized_answer,

            "score": score,

            "result": result,

            "topic": topic,

            "topic_average": round(
                topic_average,
                1
            ),

            "attempts": attempts,

            "learning_status": learning_status,

            "learning_level": learning_level,

            "recommendation": recommendation

        })

    # -----------------------------------------------------
    # GET REQUEST
    # -----------------------------------------------------

    return render_template(
        "voice.html"
    )

# =========================================================
# HANDWRITTEN ANSWER EVALUATION
# =========================================================

@app.route(
    "/handwritten",
    methods=["GET", "POST"]
)
def handwritten():

    if request.method == "POST":

        student_name = request.form.get(
            "student_name",
            ""
        ).strip()

        question = request.form.get(
            "question",
            ""
        ).strip()

        expected_answer = request.form.get(
            "expected_answer",
            ""
        ).strip()

        keywords_text = request.form.get(
            "keywords",
            ""
        ).strip()

        extracted_text = request.form.get(
            "extracted_text",
            ""
        ).strip()

        keywords = [
            item.strip()
            for item in keywords_text.split(",")
            if item.strip()
        ]

        result = evaluate_answer(
            extracted_text,
            expected_answer,
            keywords
        )

        # -------------------------------------------------
        # SAVE LEARNING PERFORMANCE
        # -------------------------------------------------

        connection = get_connection()

        cursor = connection.cursor()

        # Find student
        cursor.execute("""
            SELECT *
            FROM students
            WHERE name = ?
            LIMIT 1
        """, (
            student_name,
        ))

        student = cursor.fetchone()

        if not student and student_name:

            cursor.execute("""
                INSERT INTO students
                (
                    name,
                    email
                )
                VALUES (?, ?)
            """, (
                student_name,
                ""
            ))

            connection.commit()

            student_id = cursor.lastrowid

        elif student:

            student_id = student["id"]

        else:

            student_id = None

        # -------------------------------------------------
        # SAVE RESULT
        # -------------------------------------------------

        if student_id:

            score_value = result.get(
                "score",
                0
            )

            try:

                score_value = float(
                    score_value
                )

            except:

                score_value = 0

            # If evaluator returns /10,
            # convert it to percentage.
            if score_value <= 10:

                percentage = score_value * 10

            else:

                percentage = score_value

            cursor.execute("""
                INSERT INTO learning_performance
                (
                    student_id,
                    topic,
                    score,
                    assessment_name
                )
                VALUES (?, ?, ?, ?)
            """, (
                student_id,
                question if question else "Handwritten Assessment",
                percentage,
                "Handwritten Answer Evaluation"
            ))

            connection.commit()

        connection.close()

        return jsonify({
            "student_name": student_name,
            "question": question,
            "recognized_answer": extracted_text,
            "result": result
        })

    return render_template(
        "handwritten.html"
    )


# =========================================================
# DOCUMENT / ASSIGNMENT EVALUATION
# =========================================================

@app.route(
    "/document_evaluation",
    methods=["GET", "POST"]
)
def document_evaluation():

    if request.method == "GET":

        return render_template(
            "document_evaluation.html"
        )

    # -----------------------------------------------------
    # FORM DATA
    # -----------------------------------------------------

    student_name = request.form.get(
        "student_name",
        ""
    ).strip()

    question = request.form.get(
        "question",
        ""
    ).strip()

    expected_answer = request.form.get(
        "expected_answer",
        ""
    ).strip()

    keywords_text = request.form.get(
        "keywords",
        ""
    ).strip()

    assignment_file = request.files.get(
        "assignment_file"
    )

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not assignment_file:

        return jsonify({
            "error": "Please upload an assignment file."
        }), 400

    if assignment_file.filename == "":

        return jsonify({
            "error": "Please select a file."
        }), 400

    # -----------------------------------------------------
    # ALLOWED EXTENSIONS
    # -----------------------------------------------------

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt"
    }

    original_filename = secure_filename(
        assignment_file.filename
    )

    extension = os.path.splitext(
        original_filename
    )[1].lower()

    if extension not in allowed_extensions:

        return jsonify({
            "error": "Only PDF, DOCX and TXT files are supported."
        }), 400

    # -----------------------------------------------------
    # KEYWORDS
    # -----------------------------------------------------

    keywords = [
        item.strip()
        for item in keywords_text.split(",")
        if item.strip()
    ]

    # -----------------------------------------------------
    # TEMPORARY FILE
    # -----------------------------------------------------

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as temp_file:

            assignment_file.save(
                temp_file.name
            )

            temp_path = temp_file.name

        # -------------------------------------------------
        # EVALUATE DOCUMENT
        # -------------------------------------------------

        result = evaluate_document(
            temp_path,
            question,
            expected_answer,
            keywords
        )

        # -------------------------------------------------
        # FIND / CREATE STUDENT
        # -------------------------------------------------

        connection = get_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT *
            FROM students
            WHERE name = ?
            LIMIT 1
        """, (
            student_name,
        ))

        student = cursor.fetchone()

        if not student and student_name:

            cursor.execute("""
                INSERT INTO students
                (
                    name,
                    email
                )
                VALUES (?, ?)
            """, (
                student_name,
                ""
            ))

            connection.commit()

            student_id = cursor.lastrowid

        elif student:

            student_id = student["id"]

        else:

            student_id = None

        # -------------------------------------------------
        # DETERMINE TOPIC
        # -------------------------------------------------

        matched_concepts = result.get(
            "matched_concepts",
            []
        )

        missing_concepts = result.get(
            "missing_concepts",
            []
        )

        if matched_concepts:

            topic = matched_concepts[0]

        elif missing_concepts:

            topic = missing_concepts[0]

        else:

            topic = "General Assessment"

        # -------------------------------------------------
        # SCORE
        # -------------------------------------------------

        score = result.get(
            "score",
            0
        )

        try:

            score = float(score)

        except:

            score = 0

        # Document evaluator returns score /10.
        if score <= 10:

            percentage = score * 10

        else:

            percentage = score

        # -------------------------------------------------
        # SAVE PERFORMANCE
        # -------------------------------------------------

        if student_id:

            cursor.execute("""
                INSERT INTO learning_performance
                (
                    student_id,
                    topic,
                    score,
                    assessment_name
                )
                VALUES (?, ?, ?, ?)
            """, (
                student_id,
                topic,
                percentage,
                "Document Assignment Evaluation"
            ))

            connection.commit()

            # -------------------------------------------------
            # GET TOPIC AVERAGE
            # -------------------------------------------------

            cursor.execute("""
                SELECT
                    AVG(score) AS average_score,
                    COUNT(*) AS attempts
                FROM learning_performance
                WHERE student_id = ?
                AND topic = ?
            """, (
                student_id,
                topic
            ))

            learning_row = cursor.fetchone()

        else:

            learning_row = None

        # -------------------------------------------------
        # PERSONALIZED LEARNING
        # -------------------------------------------------

        if learning_row:

            average_score = float(
                learning_row["average_score"] or 0
            )

            attempts = learning_row["attempts"]

        else:

            average_score = percentage

            attempts = 1

        if average_score >= 80:

            status = "Strong"

            recommended_level = "Advanced"

            recommendation = (
                "Excellent performance. "
                "Try advanced questions on this topic."
            )

        elif average_score >= 60:

            status = "Needs Practice"

            recommended_level = "Intermediate"

            recommendation = (
                "You understand the basic concepts. "
                "Practice more questions to improve."
            )

        else:

            status = "Priority Learning"

            recommended_level = "Beginner"

            recommendation = (
                "Focus on the missing concepts "
                "and revise the topic before attempting "
                "advanced questions."
            )

        learning = {
            "topic": topic,
            "score": round(
                percentage,
                2
            ),
            "average_score": round(
                average_score,
                2
            ),
            "attempts": attempts,
            "status": status,
            "level": recommended_level,
            "recommendation": recommendation
        }

        connection.close()

        # -------------------------------------------------
        # FINAL RESPONSE
        # -------------------------------------------------

        return jsonify({
            "success": True,
            "student_name": student_name,
            "filename": original_filename,
            "result": result,
            "learning": learning
        })

    except Exception as error:

        return jsonify({
            "success": False,
            "error": str(error)
        }), 500

    finally:

        # -------------------------------------------------
        # DELETE TEMPORARY FILE
        # -------------------------------------------------

        if temp_path and os.path.exists(
            temp_path
        ):

            try:

                os.remove(temp_path)

            except:

                pass


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return (
        "Page not found.",
        404
    )


@app.errorhandler(405)
def method_not_allowed(error):

    return (
        "Method not allowed for this URL.",
        405
    )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    init_database()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )