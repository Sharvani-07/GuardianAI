import re


def clean_text(text):
    """Clean OCR text for evaluation."""

    text = text.lower()

    text = re.sub(r"[^a-z0-9\s]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def evaluate_answer(student_answer, expected_answer, keywords=None):
    """
    Evaluate a student's answer using keyword and text similarity.

    Returns:
        score
        matched_keywords
        missing_keywords
        feedback
    """

    student_text = clean_text(student_answer)
    expected_text = clean_text(expected_answer)

    if not student_text:
        return {
            "score": 0,
            "matched_keywords": [],
            "missing_keywords": keywords or [],
            "feedback": "No readable answer was detected."
        }

    if keywords is None:
        keywords = []

    keywords = [clean_text(word) for word in keywords]

    matched_keywords = []
    missing_keywords = []

    for keyword in keywords:

        if keyword in student_text:
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    if keywords:

        keyword_score = (
            len(matched_keywords) / len(keywords)
        ) * 10

    else:

        expected_words = set(expected_text.split())
        student_words = set(student_text.split())

        if expected_words:
            common_words = expected_words.intersection(student_words)

            keyword_score = (
                len(common_words) / len(expected_words)
            ) * 10
        else:
            keyword_score = 0

    score = round(min(keyword_score, 10), 1)

    if score >= 8:
        feedback = (
            "Excellent answer. Most important concepts "
            "are covered correctly."
        )

    elif score >= 6:
        feedback = (
            "Good answer. Some important concepts are "
            "covered, but a few points are missing."
        )

    elif score >= 4:
        feedback = (
            "Partial answer. More important concepts "
            "and explanations should be added."
        )

    else:
        feedback = (
            "The answer needs improvement. Review the "
            "topic and include the important concepts."
        )

    return {
        "score": score,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "feedback": feedback
    }
    