# eval.py
import requests
import time
import statistics
import csv
import os
from datetime import datetime

# ================= CONFIG =================
BASE_URL = "http://127.0.0.1:5000"   # or your ngrok/localtunnel URL
OUTPUT_DIR = "reports"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEST_CASES = [
    {"selection": "Collaborated", "context": "Collaborated with professor to develop a comparative analysis of credit scoring methodologies using XGBoost"},
    {"selection": "Architected", "context": "Architected GenAI solutions across banking and healthcare"},
    {"selection": "microservices", "context": "native microservices (FastAPI, Flask, Docker, Kubernetes, AWS/GCP Vertex AI) enabling scalability"},
    {"selection": "K-Means", "context": "Created customer segmentation models (K-Means, Hierarchical Clustering) to improve targeted marketing"},
    {"selection": "compliance automation", "context": "Designed compliance automation workflows reducing manual checks by 40%"}
]

REPEATS = 3

# ================= RUN TESTS =================
results = []
latencies = []
errors = 0

print("🚀 Starting evaluation...")

for case in TEST_CASES:
    for i in range(REPEATS):
        payload = {"selection": case["selection"], "context": case["context"]}
        start = time.time()
        try:
            r = requests.post(f"{BASE_URL}/meaning", json=payload, timeout=60)
            latency = time.time() - start

            if r.status_code == 200:
                meaning = r.json().get("meaning", "")
                results.append({
                    "selection": case["selection"],
                    "context": case["context"][:80] + "...",
                    "meaning": meaning,
                    "latency": round(latency, 3),
                    "status": "ok"
                })
                latencies.append(latency)
                print(f"✅ {case['selection']} | {latency:.2f}s")
            else:
                errors += 1
                results.append({
                    "selection": case["selection"],
                    "context": case["context"][:80] + "...",
                    "meaning": r.text,
                    "latency": round(latency, 3),
                    "status": f"error {r.status_code}"
                })
                print(f"❌ {case['selection']} | error {r.status_code}")
        except Exception as e:
            errors += 1
            latency = time.time() - start
            results.append({
                "selection": case["selection"],
                "context": case["context"][:80] + "...",
                "meaning": str(e),
                "latency": round(latency, 3),
                "status": "exception"
            })
            print(f"⚠️ {case['selection']} | exception {e}")

# ================= METRICS =================
mean_latency = statistics.mean(latencies) if latencies else 0
median_latency = statistics.median(latencies) if latencies else 0
p95_latency = statistics.quantiles(latencies, n=100)[94] if len(latencies) >= 20 else 0
error_rate = errors / (len(TEST_CASES) * REPEATS)

summary = f"""
Evaluation Summary ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
=================================================
Total tests: {len(TEST_CASES) * REPEATS}
Errors: {errors} ({error_rate*100:.1f}%)
Mean latency: {mean_latency:.3f}s
Median latency: {median_latency:.3f}s
95th percentile latency: {p95_latency:.3f}s
"""

print(summary)

# ================= SAVE REPORT =================
csv_path = os.path.join(OUTPUT_DIR, "eval_results.csv")
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["selection", "context", "meaning", "latency", "status"])
    writer.writeheader()
    writer.writerows(results)

txt_path = os.path.join(OUTPUT_DIR, "summary.txt")
with open(txt_path, "w", encoding="utf-8") as f:
    f.write(summary)

print(f"📊 Results saved to:\n  - {csv_path}\n  - {txt_path}")
