import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load Google API Key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in environment variables.")

# Initialize Gemini Pro model
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    google_api_key=GOOGLE_API_KEY,
    convert_system_message_to_human=True
)

# Prompt template for Sobrio
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
    return "Sobrio is live and ready to chat!"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("message", "").strip()

        if not user_input:
            return jsonify({"error": "No user input provided."}), 400

        messages = [
            SystemMessage(content=system_instruction),
            HumanMessage(content=user_input)
        ]

        response = model.invoke(messages)
        return jsonify({"response": response.content})

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({"error": "An internal error occurred. Please try again later."}), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found."}), 404

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
