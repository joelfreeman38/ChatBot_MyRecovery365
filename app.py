import os
from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Ensure environment variable is set
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in environment variables.")

# Initialize the Gemini model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="models/gemini-1.5-pro",
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }
)

# Prompt template
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

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("message", "")
        if not user_input:
            return jsonify({"error": "No input message provided."}), 400

        response = model.generate_content([
            {"role": "system", "parts": [system_instruction]},
            {"role": "user", "parts": [user_input]}
        ])

        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Serve index.html and any static files
@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(".", path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
