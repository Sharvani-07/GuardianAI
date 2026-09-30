import os
import re
from collections import Counter

from PyPDF2 import PdfReader
from docx import Document


# ============================================================
# TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf(file_path):

    text = ""

    reader = PdfReader(file_path)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def extract_text_from_docx(file_path):

    document = Document(file_path)

    text = ""

    for paragraph in document.paragraphs:

        if paragraph.text.strip():
            text += paragraph.text + "\n"

    return text


def extract_text_from_txt(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        return file.read()


def extract_text(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":

        return extract_text_from_pdf(file_path)

    elif extension == ".docx":

        return extract_text_from_docx(file_path)

    elif extension == ".txt":

        return extract_text_from_txt(file_path)

    else:

        raise ValueError(
            "Unsupported file format. "
            "Only PDF, DOCX and TXT files are supported."
        )


# ============================================================
# TEXT CLEANING
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# KEYWORD PREPARATION
# ============================================================

def prepare_keywords(keywords):

    if not keywords:
        return []

    if isinstance(keywords, list):

        keyword_list = keywords

    else:

        keyword_list = keywords.split(",")

    cleaned_keywords = []

    for keyword in keyword_list:

        keyword = keyword.strip().lower()

        if keyword:
            cleaned_keywords.append(keyword)

    return cleaned_keywords


# ============================================================
# CONCEPT MATCHING
# ============================================================

def find_concept_matches(
    student_text,
    expected_answer,
    keywords
):

    student_clean = clean_text(student_text)

    keyword_list = prepare_keywords(keywords)

    matched_keywords = []
    missing_keywords = []

    for keyword in keyword_list:

        keyword_clean = clean_text(keyword)

        if not keyword_clean:
            continue

        pattern = r"\b" + re.escape(keyword_clean) + r"\b"

        if re.search(pattern, student_clean):

            matched_keywords.append(keyword)

        else:

            missing_keywords.append(keyword)

    matched_concepts = list(matched_keywords)

    missing_concepts = list(missing_keywords)

    return {
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "matched_concepts": matched_concepts,
        "missing_concepts": missing_concepts
    }


# ============================================================
# TOKENIZATION
# ============================================================

def tokenize(text):

    text = clean_text(text)

    if not text:
        return []

    return text.split()


# ============================================================
# TEXT SIMILARITY
# ============================================================

def calculate_text_similarity(
    student_text,
    expected_answer
):

    student_words = tokenize(student_text)

    expected_words = tokenize(expected_answer)

    if not student_words or not expected_words:
        return 0

    student_counter = Counter(student_words)

    expected_counter = Counter(expected_words)

    common_words = 0

    for word in student_counter:

        if word in expected_counter:

            common_words += min(
                student_counter[word],
                expected_counter[word]
            )

    similarity = (
        common_words /
        len(expected_words)
    ) * 100

    similarity = min(
        similarity,
        100
    )

    return round(
        similarity,
        2
    )


# ============================================================
# CONCEPT COVERAGE
# ============================================================

def calculate_concept_coverage(
    matched_keywords,
    total_keywords
):

    if total_keywords == 0:
        return 0

    coverage = (
        len(matched_keywords) /
        total_keywords
    ) * 100

    return round(
        coverage,
        2
    )


# ============================================================
# ANSWER LENGTH SCORE
# ============================================================

def calculate_answer_length_score(
    student_text
):

    word_count = len(
        tokenize(student_text)
    )

    if word_count >= 150:

        return 100

    elif word_count >= 100:

        return 90

    elif word_count >= 75:

        return 80

    elif word_count >= 50:

        return 70

    elif word_count >= 25:

        return 60

    elif word_count >= 10:

        return 50

    else:

        return 30


# ============================================================
# FINAL SCORE
# ============================================================

def calculate_score(
    concept_coverage,
    similarity,
    answer_length
):

    score = (

        (concept_coverage * 0.50) +
        (similarity * 0.30) +
        (answer_length * 0.20)

    )

    score = max(
        0,
        min(
            score,
            100
        )
    )

    score_out_of_10 = score / 10

    return round(
        score_out_of_10,
        2
    )


# ============================================================
# FEEDBACK
# ============================================================

def generate_feedback(
    score,
    matched_keywords,
    missing_keywords,
    similarity,
    concept_coverage
):

    feedback = []

    if score >= 8:

        feedback.append(
            "Excellent understanding of the topic."
        )

    elif score >= 6:

        feedback.append(
            "Good understanding, but some concepts need improvement."
        )

    elif score >= 4:

        feedback.append(
            "Basic understanding is present, but several concepts need revision."
        )

    else:

        feedback.append(
            "The answer needs significant improvement and concept revision."
        )

    if matched_keywords:

        feedback.append(
            "Important concepts identified: "
            + ", ".join(matched_keywords)
            + "."
        )

    if missing_keywords:

        feedback.append(
            "Concepts that need attention: "
            + ", ".join(missing_keywords)
            + "."
        )

    if similarity >= 80:

        feedback.append(
            "The answer is closely related to the reference answer."
        )

    elif similarity >= 50:

        feedback.append(
            "The answer is partially related to the reference answer."
        )

    else:

        feedback.append(
            "The answer has limited similarity to the reference answer."
        )

    if concept_coverage >= 80:

        feedback.append(
            "Most important concepts were covered."
        )

    elif concept_coverage >= 50:

        feedback.append(
            "Some important concepts were covered, but more concepts should be included."
        )

    else:

        feedback.append(
            "Several important concepts are missing."
        )

    return " ".join(feedback)


# ============================================================
# PERSONALIZED RECOMMENDATION
# ============================================================

def generate_recommendation(
    score,
    missing_keywords
):

    if score >= 8:

        recommendation = (
            "Personalized Learning Recommendation: "
            "The student demonstrates strong understanding. "
            "Provide advanced questions and application-based problems."
        )

    elif score >= 6:

        recommendation = (
            "Personalized Learning Recommendation: "
            "The student has a reasonable understanding. "
            "Provide practice questions focusing on the missing concepts."
        )

    elif score >= 4:

        recommendation = (
            "Personalized Learning Recommendation: "
            "The student needs additional practice. "
            "Revise the basic concepts and attempt beginner-level questions."
        )

    else:

        recommendation = (
            "Personalized Learning Recommendation: "
            "The student needs focused learning support. "
            "Start with basic explanations and beginner-level questions."
        )

    if missing_keywords:

        recommendation += (
            " Focus especially on: "
            + ", ".join(missing_keywords)
            + "."
        )

    return recommendation


# ============================================================
# LEARNING GAPS
# ============================================================

def generate_learning_gaps(
    missing_keywords
):

    learning_gaps = []

    for keyword in missing_keywords:

        learning_gaps.append({

            "concept": keyword,

            "status": "Needs Learning",

            "recommendation":
                "Revise the concept and practice related questions."

        })

    return learning_gaps


# ============================================================
# MAIN EVALUATION FUNCTION
# ============================================================

def evaluate_document(
    file_path,
    question,
    expected_answer,
    keywords
):

    extracted_text = extract_text(
        file_path
    )

    extracted_text = extracted_text.strip()

    if not extracted_text:

        raise ValueError(
            "No readable text was found in the uploaded document."
        )

    keyword_list = prepare_keywords(
        keywords
    )

    concept_result = find_concept_matches(
        extracted_text,
        expected_answer,
        keyword_list
    )

    matched_keywords = concept_result[
        "matched_keywords"
    ]

    missing_keywords = concept_result[
        "missing_keywords"
    ]

    matched_concepts = concept_result[
        "matched_concepts"
    ]

    missing_concepts = concept_result[
        "missing_concepts"
    ]

    similarity = calculate_text_similarity(
        extracted_text,
        expected_answer
    )

    concept_coverage = calculate_concept_coverage(
        matched_keywords,
        len(keyword_list)
    )

    answer_length = calculate_answer_length_score(
        extracted_text
    )

    score = calculate_score(
        concept_coverage,
        similarity,
        answer_length
    )

    feedback = generate_feedback(
        score,
        matched_keywords,
        missing_keywords,
        similarity,
        concept_coverage
    )

    recommendation = generate_recommendation(
        score,
        missing_keywords
    )

    learning_gaps = generate_learning_gaps(
        missing_keywords
    )

    return {

        "question": question,

        "score": score,

        "coverage": concept_coverage,

        "concept_coverage": concept_coverage,

        "similarity": similarity,

        "answer_length": answer_length,

        "matched_keywords": matched_keywords,

        "matched_concepts": matched_concepts,

        "missing_keywords": missing_keywords,

        "missing_concepts": missing_concepts,

        "learning_gaps": learning_gaps,

        "feedback": feedback,

        "recommendation": recommendation,

        "extracted_text": extracted_text
    }