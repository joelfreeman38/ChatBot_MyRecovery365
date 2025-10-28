from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
from google.generativeai import GenerativeModel
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai

# === Environment variable check ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in environment variables.")

# === Configure Gemini Pro 2.5 ===
genai.configure(api_key=GEMINI_API_KEY)
model = GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    }
)

# === Sobrio system prompt ===
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

# === Flask App ===
app = Flask(__name__)
CORS(app)

# === HTML UI Template ===
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sobrio Sober Coach</title>
    <style>
        body {
            background: #f7f8fa;
            font-family: 'Segoe UI', sans-serif;
            margin: 0;
            padding: 40px;
        }
        .chat-container {
            max-width: 720px;
            margin: auto;
            background: #fff;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
        }
        textarea {
            width: 100%;
            padding: 12px;
            font-size: 1rem;
            resize: none;
            border-radius: 8px;
            border: 1px solid #ccc;
        }
        button {
            margin-top: 10px;
            width: 100%;
            padding: 12px;
            font-size: 1rem;
            background-color: #007bff;
            color: #fff;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }
        .response {
            margin-top: 20px;
            padding: 18px;
            background-color: #e6f3ff;
            border-left: 4px solid #007bff;
            border-radius: 6px;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <h1>Sobrio AI Sober Coach</h1>
        <form method="post">
            <textarea name="user_input" placeholder="Type your question here..." required></textarea>
            <button type="submit">Ask Sobrio</button>
        </form>
        {% if response %}
        <div class="response">
            <strong>Sobrio:</strong><br>
            {{ response }}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

# === Routes ===

@app.route("/", methods=["GET", "POST"])
def chat_ui():
    response = ""
    if request.method == "POST":
        user_input = request.form.get("user_input", "")
        try:
            gemini_response = model.generate_content([
                {"role": "system", "parts": [system_instruction]},
                {"role": "user", "parts": [user_input]}
            ])
            response = gemini_response.text
        except Exception as e:
            response = f"An error occurred: {str(e)}"
    return render_template_string(HTML_TEMPLATE, response=response)

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    user_input = data.get("user_input")
    if not user_input:
        return jsonify({"error": "Missing user_input"}), 400
    try:
        gemini_response = model.generate_content([
            {"role": "system", "parts": [system_instruction]},
            {"role": "user", "parts": [user_input]}
        ])
        return jsonify({"response": gemini_response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === Local run only ===
if __name__ == "__main__":
    app.run(debug=True)
