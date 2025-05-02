import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)
CORS(app)

model = genai.GenerativeModel("gemini-1.5-flash")

CRISIS_KEYWORDS = [
    "suicidal", "kill myself", "end it all", "self-harm", "cutting", "can’t go on",
    "jump off", "overdose", "hang myself", "no way out", "ending it", "want to die"
]

CRISIS_RESPONSE = (
    "It sounds like you're going through an incredibly difficult time. "
    "You're not alone, and there is help available.

"
    "**If you're in the U.S.**, please call or text **988** for the Suicide & Crisis Lifeline.
"
    "**In Canada**, call **1-833-456-4566**.
"
    "**In the U.K.**, contact **Samaritans at 116 123**.
"
    "**Find international resources:** https://findahelpline.com/

"
    "Would you like to talk more about what's on your mind right now?"
)

def detect_crisis(text):
    lowered = text.lower()
    return any(keyword in lowered for keyword in CRISIS_KEYWORDS)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")

    if detect_crisis(user_input):
        return jsonify({"response": CRISIS_RESPONSE})

    try:
        response = model.generate_content(user_input)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"response": "There was an error generating a response. Please try again later."}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8000)