import json
import csv
import subprocess
import os
import re

OLLAMA = os.path.join(
    os.environ["LOCALAPPDATA"],
    "Programs", "Ollama", "ollama.exe"
)

# Load questions
with open("golden_set.json", "r", encoding="utf-8") as file:
    questions = json.load(file)

results = []

for item in questions:
    question = item["question"]
    expected = item["expected_answer"]

    print("\nQuestion:", question)

    # Get answer from Llama 3.2
    result = subprocess.run(
        [OLLAMA, "run", "llama3.2", question],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180
    )

    answer = result.stdout.strip()

    if result.returncode != 0:
        print("Ollama error:", result.stderr)
        continue

    # Keyword-based evaluation
    keywords = set(
        re.findall(r"\b[a-zA-Z]{4,}\b", expected.lower())
    )

    answer_words = set(
        re.findall(r"\b[a-zA-Z]{4,}\b", answer.lower())
    )

    matched = keywords.intersection(answer_words)

    score = (
        len(matched) / len(keywords) * 100
        if keywords else 0
    )

    print("Answer:", answer)
    print("Score:", round(score, 2), "%")

    results.append({
        "question": question,
        "expected_answer": expected,
        "generated_answer": answer,
        "score": round(score, 2)
    })

# Save results to CSV
with open(
    "baseline_results.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "question",
            "expected_answer",
            "generated_answer",
            "score"
        ]
    )
    writer.writeheader()
    writer.writerows(results)

print("\nEvaluation completed!")
print("Results saved in baseline_results.csv")
