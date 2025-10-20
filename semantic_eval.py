import requests
import time
import csv
from datetime import datetime
import statistics

# 📦 Install needed packages first:
# pip install nltk rouge-score bert-score sentence-transformers

import nltk
from rouge_score import rouge_scorer
from bert_score import score as bert_score
from sentence_transformers import SentenceTransformer, util

nltk.download('punkt', quiet=True)

# ================== CONFIG ==================
API_URL = "http://127.0.0.1:5000/meaning"   # Flask endpoint
REPEATS = 1                                 # times per query for averaging

# Example gold references (ground truth)
TEST_SET = [
    {
        "selection": "Collaborated",
        "context": "Collaborated with professor to develop a comparative analysis of credit scoring methodologies using XGBoost",
        "reference": "Worked together with the professor as a team to conduct a comparative analysis of credit scoring approaches using XGBoost."
    },
    {
        "selection": "Architected",
        "context": "Architected GenAI solutions across banking and healthcare...",
        "reference": "Designed and structured complex GenAI solutions for banking and healthcare systems."
    },
    {
        "selection": "microservices",
        "context": "native microservices (FastAPI, Flask, Docker, Kubernetes, AWS/GCP Vertex AI) enabling 99.95% availability...",
        "reference": "A software architecture approach where applications are built as a collection of small, independent services that communicate with each other."
    },
    {
        "selection": "K-Means",
        "context": "Created customer segmentation models (K-Means, Hierarchical Clustering)...",
        "reference": "An unsupervised machine learning algorithm that groups data points into k clusters based on similarity."
    },
    {
        "selection": "compliance automation",
        "context": "Designed compliance automation workflows reducing manual checks by 40%...",
        "reference": "Using technology to automatically enforce regulatory checks and compliance processes, reducing manual effort and errors."
    }
]

# Load sentence embeddings model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ================== HELPERS ==================
def compute_metrics(pred, ref):
    """Compute BLEU, ROUGE, BERTScore, Cosine Similarity"""
    # BLEU
    ref_tokens = [nltk.word_tokenize(ref.lower())]
    pred_tokens = nltk.word_tokenize(pred.lower())
    bleu = nltk.translate.bleu_score.sentence_bleu(ref_tokens, pred_tokens)

    # ROUGE-L
    rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    rouge_score_val = rouge.score(ref, pred)["rougeL"].fmeasure

    # BERTScore (F1 only, avg)
    P, R, F1 = bert_score([pred], [ref], lang="en", verbose=False)
    bert = F1.mean().item()

    # Cosine similarity (embeddings)
    emb_pred = embedder.encode(pred, convert_to_tensor=True)
    emb_ref = embedder.encode(ref, convert_to_tensor=True)
    cosine = util.pytorch_cos_sim(emb_pred, emb_ref).item()

    return bleu, rouge_score_val, bert, cosine


# ================== MAIN EVAL ==================
def run_evaluation():
    rows = []
    latencies = []

    print("🚀 Starting semantic evaluation...")

    for test in TEST_SET:
        selection, context, reference = test["selection"], test["context"], test["reference"]

        for r in range(REPEATS):
            try:
                start = time.time()
                resp = requests.post(API_URL, json={"selection": selection, "context": context}, timeout=30)
                latency = time.time() - start

                if resp.status_code == 200:
                    meaning = resp.json().get("meaning", "")
                    bleu, rouge, bert, cosine = compute_metrics(meaning, reference)

                    rows.append([selection, reference, meaning, f"{bleu:.3f}", f"{rouge:.3f}", f"{bert:.3f}", f"{cosine:.3f}", f"{latency:.3f}", "ok"])
                    latencies.append(latency)

                    print(f"✅ {selection} | BLEU={bleu:.3f}, ROUGE-L={rouge:.3f}, BERTScore={bert:.3f}, Cosine={cosine:.3f}, Lat={latency:.2f}s")

                else:
                    rows.append([selection, reference, "ERROR", "0", "0", "0", "0", "0", f"HTTP {resp.status_code}"])
                    print(f"❌ {selection} | HTTP {resp.status_code}")

            except Exception as e:
                rows.append([selection, reference, "EXCEPTION", "0", "0", "0", "0", "0", str(e)])
                print(f"⚠️ {selection} | exception {e}")

    # Save CSV
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = f"semantic_eval_{ts}.csv"
    with open(out_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["selection", "reference", "prediction", "BLEU", "ROUGE-L", "BERTScore", "CosineSim", "latency", "status"])
        writer.writerows(rows)

    # Summary
    if latencies:
        print("\n📊 Evaluation Summary")
        print("="*50)
        print(f"Total tests: {len(rows)}")
        print(f"Errors: {len([r for r in rows if r[-1] != 'ok'])}")
        print(f"Mean latency: {statistics.mean(latencies):.3f}s")
        print(f"Median latency: {statistics.median(latencies):.3f}s")
        print(f"p95 latency: {statistics.quantiles(latencies, n=100)[94]:.3f}s")
        print(f"CSV saved: {out_file}")


if __name__ == "__main__":
    run_evaluation()
