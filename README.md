📘 Meaning-PDF: Contextual Word Explanations in PDFs

This project allows users to upload a PDF, select words/phrases, and get context-aware explanations using an LLM (via Groq API
).

It also includes an evaluation pipeline with BLEU, ROUGE, BERTScore, and semantic similarity metrics.

🚀 Features

Upload PDF and view inside browser.

Highlight/select words → get context-aware meaning.

History tab of all past queries.

Backend powered by Flask + Groq API.

Semantic evaluation (BLEU, ROUGE, BERTScore, cosine similarity).

Export results to CSV.

⚙️ Setup Instructions
1️⃣ Clone Repo
git clone https://github.com/your-username/Meaning_PDF.git
cd Meaning_PDF

2️⃣ Create Virtual Environment
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt


If requirements.txt is missing, here’s the essentials:

pip install flask transformers torch groq requests nltk sentence-transformers bert-score rouge-score

4️⃣ Install NLTK Data
python -m nltk.downloader punkt punkt_tab

5️⃣ Set Groq API Key

Get your API key from Groq Console
.

export GROQ_API_KEY="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" 

▶️ Run Application
python app.py


Then open browser at:

http://127.0.0.1:5000


Upload a PDF, highlight a word, and see its contextual meaning.

📊 Run Evaluation

To test against gold references:

python semantic_eval.py


This will:

Send multiple test queries

Measure BLEU, ROUGE, BERTScore, cosine similarity, and latency

Save results to semantic_eval_<timestamp>.csv

📈 Example Results

Last run (2025-09-23):

Evaluation Summary
==================================================
Total tests: 5
Errors: 0
Mean latency: 0.682s
Median latency: 0.622s
p95 latency: 1.070s


Sample Metrics:

Term	BLEU	ROUGE-L	BERTScore	Cosine	Latency
Collaborated	0.068	0.255	0.876	0.528	0.62s
Architected	0.000	0.157	0.854	0.580	0.91s
microservices	0.034	0.159	0.871	0.458	0.68s
K-Means	0.039	0.211	0.881	0.589	0.61s
compliance automation	0.000	0.196	0.876	0.762	0.59s
📝 Notes

BLEU scores may be low (strict n-gram matching).

BERTScore + cosine similarity are better indicators of semantic correctness.

Use GPU (CUDA) for faster inference.