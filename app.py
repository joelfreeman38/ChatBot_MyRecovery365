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

@app.route("/chat-ui", methods=["GET"])
def chat_ui():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MR-365 Chatbot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f4f4;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
            }
            h2 {
                color: #333;
            }
            #chat-box {
                width: 100%;
                max-width: 600px;
                height: 400px;
                background: white;
                border: 1px solid #ccc;
                border-radius: 10px;
                overflow-y: auto;
                padding: 15px;
                margin-bottom: 10px;
            }
            .message {
                margin-bottom: 10px;
            }
            .user {
                text-align: right;
                color: blue;
            }
            .bot {
                text-align: left;
                color: green;
            }
            input[type="text"] {
                width: 100%;
                max-width: 600px;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
                border: 1px solid #ccc;
            }
        </style>
    </head>
    <body>
        <h2>Talk to MR-365 Sober Coach</h2>
        <div id="chat-box"></div>
        <input type="text" id="user-input" placeholder="Type your message here..." onkeypress="handleKey(event)">
        
        <script>
            const chatBox = document.getElementById('chat-box');
            const input = document.getElementById('user-input');

            function appendMessage(message, sender) {
                const div = document.createElement('div');
                div.classList.add('message', sender);
                div.textContent = message;
                chatBox.appendChild(div);
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            function handleKey(event) {
                if (event.key === 'Enter') {
                    const message = input.value;
                    appendMessage("You: " + message, "user");
                    input.value = "";
                    fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message })
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.response) {
                            appendMessage("MR-365: " + data.response, "bot");
                        } else {
                            appendMessage("Error: " + data.error, "bot");
                        }
                    });
                }
            }
        </script>
    </body>
    </html>
    """)

@app.route("/", methods=["GET"])
def index():
    return "<h3>MR-365 Chatbot is running.</h3>"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)




