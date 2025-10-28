import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from google.generativeai import configure, GenerativeModel

app = Flask(__name__)
CORS(app)

# Load Google API key from environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in environment variables.")

# Set up Google Generative AI
configure(api_key=GOOGLE_API_KEY)

# Use Gemini Pro 2.5 model
model = GenerativeModel("gemini-1.5-pro-latest")

# Improved prompt template
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

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Sobrio AI Coach is running."})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("message", "").strip()

        if not user_input:
            return jsonify({"error": "No input provided."}), 400

        response = model.generate_content([
            {"role": "system", "parts": [system_instruction]},
            {"role": "user", "parts": [user_input]}
        ])

        output_text = response.text.strip() if hasattr(response, 'text') else "Sorry, I didn't understand that."

        return jsonify({"response": output_text})

    except Exception as e:
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
