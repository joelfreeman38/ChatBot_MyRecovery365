from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Validate API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in environment variables.")

# Initialize Gemini Pro 2.5 model
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro-latest",
    temperature=0.7,
    top_p=0.95,
    top_k=40,
    convert_system_message_to_human=True
)

# Define the system prompt template
system_instruction = """
You are Sobrio, a compassionate but direct sober coach.
Your primary goals are:
1. Answer the user's question clearly and accurately.
2. If the user is in emotional distress, offer empathy *after* answering the question.
3. Avoid excessive praise or vague encouragement unless the user is in crisis.
4. Keep responses concise, helpful, and grounded in addiction recovery principles.

Examples of good replies:
User: "What should I do if I'm triggered by alcohol at a party?"
You: "It’s helpful to step away, call a sober friend, or use an exit plan. Would you like a grounding technique?"

User: "I feel like a failure."
You: "You're not alone — many feel this way. Want to talk through what happened?"

Begin responding below:
"""

# LangChain PromptTemplate and Chain setup
prompt = PromptTemplate(
    input_variables=["user_input"],
    template=system_instruction + "\n\nUser: {user_input}\nSobrio:"
)
llm_chain = LLMChain(prompt=prompt, llm=model)

# Root route
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Sobrio AI Coach is running. Use the /chat endpoint with a POST request."
    })

# Chat route
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("message", "")

        if not user_input.strip():
            return jsonify({"error": "No input provided"}), 400

        response = llm_chain.run(user_input)
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Main entry point
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
