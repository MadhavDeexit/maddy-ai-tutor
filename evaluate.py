import csv
import time
from tutor import AITutor

# (question, expected topic). Questions are paraphrased on purpose.
TEST_CASES = [
    ("Explain AI to me", "Artificial Intelligence"),
    ("How do machines mimic human intelligence?", "Artificial Intelligence"),
    ("Define artificial intelligence", "Artificial Intelligence"),

    ("How do computers learn from data?", "Machine Learning"),
    ("Tell me about ML", "Machine Learning"),
    ("What is machine learning used for?", "Machine Learning"),

    ("What is deep learning?", "Deep Learning"),
    ("How do multi-layer networks learn?", "Deep Learning"),
    ("Explain deep neural learning", "Deep Learning"),

    ("What are neural networks?", "Neural Networks"),
    ("How do artificial neurons work?", "Neural Networks"),
    ("Explain neural net architecture", "Neural Networks"),

    ("What is cybersecurity?", "Cybersecurity"),
    ("How do I protect a network from hackers?", "Cybersecurity"),
    ("Explain information security", "Cybersecurity"),

    ("What is encryption?", "Encryption"),
    ("How does AES protect data?", "Encryption"),
    ("Explain how data is encoded to keep it secret", "Encryption"),

    ("What is Python?", "Python"),
    ("Tell me about the Python programming language", "Python"),
    ("Why do developers use Python?", "Python"),

    ("What is blockchain?", "Blockchain"),
    ("How does a distributed ledger work?", "Blockchain"),
    ("Explain chained blocks of transactions", "Blockchain"),

    ("What is cloud computing?", "Cloud Computing"),
    ("Explain AWS and Azure", "Cloud Computing"),
    ("How are servers delivered over the internet?", "Cloud Computing"),

    ("What is data science?", "Data Science"),
    ("How do analysts extract insights from data?", "Data Science"),
    ("Explain the field of data science", "Data Science"),

    ("What is NLP?", "NLP"),
    ("How do computers understand human language?", "NLP"),
    ("Explain natural language processing", "NLP"),

    ("What is computer vision?", "Computer Vision"),
    ("How do machines understand images?", "Computer Vision"),
    ("Explain image recognition by computers", "Computer Vision"),

    # Out-of-scope questions: should trigger the fallback
    ("What is pizza?", "Out of scope"),
    ("Who won the cricket match yesterday?", "Out of scope"),
    ("How do I cook rice?", "Out of scope"),
    ("What is the capital of France?", "Out of scope"),
    ("Tell me a joke", "Out of scope"),
    ("What is the weather today?", "Out of scope"),
]


def main():
    tutor = AITutor()
    rows = []
    correct = 0
    total_time = 0

    print("\nRunning evaluation...\n")
    for question, expected in TEST_CASES:
        start = time.time()
        _, confidence, predicted = tutor.answer_question(question)
        ms = int((time.time() - start) * 1000)
        total_time += ms

        ok = predicted == expected
        correct += ok
        rows.append([question, expected, predicted, confidence, ms, "PASS" if ok else "FAIL"])

    # Print table
    print(f"{'Question':<50}{'Expected':<24}{'Predicted':<24}{'Conf':<7}{'ms':<6}Result")
    print("-" * 120)
    for r in rows:
        print(f"{r[0][:48]:<50}{r[1]:<24}{r[2]:<24}{str(r[3]) + '%':<7}{r[4]:<6}{r[5]}")

    n = len(TEST_CASES)
    in_scope = [r for r in rows if r[1] != "Out of scope"]
    out_scope = [r for r in rows if r[1] == "Out of scope"]
    in_acc = sum(r[5] == "PASS" for r in in_scope) / len(in_scope) * 100
    out_acc = sum(r[5] == "PASS" for r in out_scope) / len(out_scope) * 100

    print("\n" + "=" * 40)
    print(f"Total test questions     : {n}")
    print(f"Overall accuracy         : {correct / n * 100:.1f}%")
    print(f"In-scope accuracy        : {in_acc:.1f}%")
    print(f"Out-of-scope rejection   : {out_acc:.1f}%")
    print(f"Average response time    : {total_time / n:.0f} ms")
    print("=" * 40)

    # Save results for your report/slides
    with open("evaluation_results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Question", "Expected", "Predicted", "Confidence", "Time_ms", "Result"])
        writer.writerows(rows)
    print("\nSaved: evaluation_results.csv")


if __name__ == "__main__":
    main()