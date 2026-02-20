import json
from src.answering.answer_query import answer_query


# -----------------------------------------
# Test Questions (Policy-specific)
# -----------------------------------------
TEST_QUESTIONS = [
    "What is the scope of this policy?",
    "How are third-party vendors managed?",
    "What is the purpose of the compliance section?",
    "How is disaster recovery handled?",
    "What are the responsibilities in vendor contracts?"
]


def evaluate_answer(question, result):
    """
    Evaluate a single answer output.
    """

    answer = result["answer"]
    confidence = result["confidence_score"]
    sources = result["sources"]

    evaluation = {
        "question": question,
        "answer_length": len(answer),
        "num_sources": len(sources),
        "confidence_score": confidence,
        "confidence_level": result["confidence_level"],
        "potential_issue": None
    }

    # ---- Basic Enterprise Checks ----

    if len(answer.strip()) == 0:
        evaluation["potential_issue"] = "Empty answer"

    elif confidence < 0.5:
        evaluation["potential_issue"] = "Low confidence"

    elif len(sources) == 0:
        evaluation["potential_issue"] = "No citation source"

    elif "not available" in answer.lower():
        evaluation["potential_issue"] = "Model could not find answer"

    else:
        evaluation["potential_issue"] = "OK"

    return evaluation


def run_full_evaluation():
    """
    Run evaluation on all test questions.
    """

    results = []

    print("\n==============================")
    print("RUNNING SYSTEM EVALUATION")
    print("==============================\n")

    for question in TEST_QUESTIONS:

        print(f"Testing: {question}")

        result = answer_query(question)

        evaluation = evaluate_answer(question, result)

        results.append(evaluation)

        print("Confidence:", evaluation["confidence_score"])
        print("Status:", evaluation["potential_issue"])
        print("-" * 40)

    print("\n==============================")
    print("EVALUATION SUMMARY")
    print("==============================\n")

    print(json.dumps(results, indent=4))


if __name__ == "__main__":
    run_full_evaluation()
