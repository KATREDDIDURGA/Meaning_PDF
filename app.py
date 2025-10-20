# from flask import Flask, render_template, request, send_from_directory, jsonify
# import os
# import re
# from groq import Groq   # ✅ Groq official client

# # ================== CONFIG ==================
# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MODEL_NAME = "llama-3.1-8b-instant"   # 🔹 default choice (fast + good quality)
# GROQ_API_KEY = os.environ.get("GROQ_API_KEY")  # 🔑 set this in your env

# if not GROQ_API_KEY:
#     raise ValueError("⚠️ Please set your GROQ_API_KEY environment variable.")

# # Init Flask + Groq client
# app = Flask(__name__)
# client = Groq(api_key=GROQ_API_KEY)

# # ================== ROUTES ==================
# @app.route("/")
# def index():
#     return render_template("index.html")

# # 🔹 Upload endpoint
# @app.route("/upload", methods=["POST"])
# def upload_file():
#     file = request.files["file"]
#     if file.filename.endswith(".pdf"):
#         filepath = os.path.join(UPLOAD_FOLDER, file.filename)
#         file.save(filepath)
#         return {"filename": file.filename}
#     return {"error": "Only PDF files allowed"}, 400

# # 🔹 Serve uploaded PDFs
# @app.route("/pdf/<filename>")
# def serve_pdf(filename):
#     return send_from_directory(UPLOAD_FOLDER, filename)

# # 🔹 Semantic meaning endpoint
# @app.route("/meaning", methods=["POST"])
# def meaning():
#     data = request.json
#     selection = data.get("selection", "").strip()
#     context = data.get("context", "")

#     # ✅ Clean selection
#     selection = re.sub(r"[^a-zA-Z0-9\- ]", "", selection)
#     if not selection or len(selection.split()) < 1:
#         return jsonify({"meaning": "⚠️ Invalid or too short selection"}), 400

#     # ✅ Limit context length
#     context_words = context.split()
#     context = " ".join(context_words[:80])  # keep ~80 words max

#     # Build a nice instruction prompt
#     prompt = f"Explain the meaning of '{selection}' in this context:\n\n{context}\n\n"

#     print(f"⚡ Prompt: {prompt}")  # debug log

#     try:
#         # 🔹 Call Groq API (chat.completions)
#         response = client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=[
#                 {"role": "system", "content": "You are an AI assistant that explains words and phrases in context clearly and concisely."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=500,
#             temperature=0.3
#         )

#         meaning_text = response.choices[0].message.content.strip()
#         return jsonify({"meaning": meaning_text})

#     except Exception as e:
#         print("❌ Error:", e)
#         return jsonify({"error": str(e)}), 500

# # ================== MAIN ==================
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)


from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import re
from groq import Groq

# ================== CONFIG ==================
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MODEL_NAME = "llama-3.1-8b-instant"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("⚠️ Please set your GROQ_API_KEY environment variable.")

# Init Flask + Groq client
app = Flask(__name__)
client = Groq(api_key=GROQ_API_KEY)

# ================== ROUTES ==================
@app.route("/")
def index():
    return render_template("index.html")

# 🔹 Upload endpoint
@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    if file.filename.endswith(".pdf"):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        return {"filename": file.filename}
    return {"error": "Only PDF files allowed"}, 400

# 🔹 Serve uploaded PDFs
@app.route("/pdf/<filename>")
def serve_pdf(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# 🔹 Semantic meaning endpoint with language support
@app.route("/meaning", methods=["POST"])
def meaning():
    data = request.json
    selection = data.get("selection", "").strip()
    context = data.get("context", "")
    language = data.get("language", "English")  # ✅ New: language parameter

    # ✅ Clean selection
    selection = re.sub(r"[^a-zA-Z0-9\- ]", "", selection)
    if not selection or len(selection.split()) < 1:
        return jsonify({"meaning": "⚠️ Invalid or too short selection"}), 400

    # ✅ Limit context length
    context_words = context.split()
    context = " ".join(context_words[:80])

    # ✅ Build prompt with strong language instruction
    if language and language.lower() != "english":
        prompt = f"""You must respond ONLY in {language} language. Do not use English.

Word/Phrase to explain: '{selection}'

Context: {context}

Provide a clear explanation of what '{selection}' means in this context. Write your entire response in {language}."""
        system_message = f"You are a helpful assistant. You MUST respond entirely in {language}. Never use English. Always write your complete response in {language} language only."
    else:
        prompt = f"Explain the meaning of '{selection}' in this context:\n\n{context}\n\n"
        system_message = "You are an AI assistant that explains words and phrases in context clearly and concisely."

    print(f"⚡ Language: {language} | Prompt: {prompt}")

    try:
        # 🔹 Call Groq API
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )

        meaning_text = response.choices[0].message.content.strip()
        return jsonify({"meaning": meaning_text, "language": language})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500

# ================== MAIN ==================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)