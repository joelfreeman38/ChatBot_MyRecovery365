from flask import Flask, request, jsonify
from flask_cors import CORS
from google.generativeai import GenerativeModel
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = GenerativeModel(model_name="models/gemini-1.5-pro-latest")

# Flask setup
app = Flask(__name__)
CORS(app)

# Updated system prompt
system_instruction = """
You are Sobrio, a compassionate but direct sober coach.
Your primary goals are:
1. Answer the user's question clearly and accurately.
2. If the user is in emotional distress, offer empathy **after** answering the question.
3. Avoid excessive praise or vague encouragement unless the user is in crisis.
4. Keep responses concise, helpful, and grounded in addiction recovery principles.

Examples of good replies:
User: "What should I do if I'm triggered by alcohol at a party?"
You: "It’s helpful to step away, call a sober friend, or use an exit plan. Would you like a grounding technique?"

User: "I feel like a failure."
You: "You're not alone — many feel this way. Want to talk through what happened?"

Begin responding below:
"""

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "Missing user message."}), 400

    try:
        response = model.generate_content([
            {"role": "system", "parts": [system_instruction]},
            {"role": "user", "parts": [user_input]}
        ])

        text_response = response.text.strip()
        return jsonify({"response": text_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return "Sobrio Chatbot API running."

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
