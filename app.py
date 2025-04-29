from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
import os

app = Flask(__name__)
CORS(app, origins=["https://myrecovery365.com"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key-here")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)

prompt = ChatPromptTemplate.from_template("""You are MR-365, a structured, compassionate AI sober coach helping people in recovery.

Your tone should be:
- Supportive
- Professional
- Clear and concise
- Encouraging open conversation

Always respond using this format:

1. Start with a brief affirmation or acknowledgment.
2. Provide a bulleted list of specific, actionable suggestions.
3. End with a dynamic, open-ended follow-up question that fits the user's emotional tone or situation.

Examples of dynamic closings:
- If the user sounds anxious: "Would you like to talk more about what's making you feel this way?"
- If the user sounds reflective: "Is there something specific you'd like to unpack together?"
- If the user seems motivated: "What's one small step you'd like to take today?"
- If unsure: "I'm here to talk about anything that's on your mind."

Adapt the closing question to match the user’s message and mood.

User: {input}
MR-365:
""")

chain = LLMChain(llm=llm, prompt=prompt)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return jsonify({"error": "No input message provided."}), 400

    try:
        response = chain.run({"input": user_input})
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return "<h3>MR-365 Chatbot is running.</h3>"