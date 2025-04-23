from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ Import CORS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
import os

app = Flask(__name__)

# ✅ Lock CORS to your WordPress site only
CORS(app, origins=["https://myrecovery365.com"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key-here")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)

prompt = ChatPromptTemplate.from_template("""
You are MR-365, a compassionate AI sober coach that supports individuals recovering from addiction.
Respond in a supportive and non-judgmental tone.
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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


