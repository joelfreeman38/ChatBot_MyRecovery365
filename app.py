from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
import os

app = Flask(__name__)
CORS(app, origins=["https://myrecovery365.com"])

# Set up Gemini / Google API for MR-365 chatbot
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key-here")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY)

# Prompt template for MR-365
prompt = ChatPromptTemplate.from_template("""
You are MR-365, a compassionate AI sober coach that supports individuals recovering from addiction.
Respond in a supportive and non-judgmental tone.
User: {input}
MR-365:
""")

chain = LLMChain(llm=llm, prompt=prompt)

# POST route to handle chat messages
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

# UI chat interface for iframe or full-page display
@app.route("/chat-ui", methods=["GET"])
def chat_ui():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MR-365 Sober Coach</title>
        <style>
            body {
                font-family: 'Segoe UI', sans-serif;
                margin: 0;
                background-color: #f2f2f2;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
            }

            h2 {
                margin-bottom: 10px;
                color: #333;
            }

            #chat-box {
                width: 100%;
                max-width: 700px;
                height: 450px;
                background: white;
                border-radius: 12px;
                border: 1px solid #ddd;
                overflow-y: auto;
                padding: 20px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                margin-bottom: 10px;
            }

            .message {
                display: flex;
                margin-bottom: 15px;
            }

            .user {
                justify-content: flex-end;
            }

            .bot {
                justify-content: flex-start;
            }

            .bubble {
                max-width: 70%;
                padding: 12px 16px;
                border-radius: 20px;
                font-size: 1.05rem;
                line-height: 1.4;
            }

            .user .bubble {
                background-color: #007bff;
                color: white;
                border-bottom-right-radius: 5px;
            }

            .bot .bubble {
                background-color: #e4e6eb;
                color: #111;
                border-bottom-left-radius: 5px;
            }

            .avatar {
                width: 36px;
                height: 36px;
                border-radius: 50%;
                margin: 0 10px;
                background-size: cover;
                background-position: center;
            }

            .user .avatar {
                background-image: url('https://cdn-icons-png.flaticon.com/512/1946/1946429.png');
            }

            .bot .avatar {
                background-image: url('https://cdn-icons-png.flaticon.com/512/4712/4712106.png');
            }

            #user-input {
                width: 100%;
                max-width: 700px;
                padding: 15px;
                font-size: 1.1rem;
                border-radius: 8px;
                border: 1px solid #ccc;
                box-sizing: border-box;
            }

            @media screen and (max-width: 600px) {
                #chat-box {
                    height: 400px;
                }
                .bubble {
                    font-size: 1rem;
                }
            }
        </style>
    </head>
    <body>
        <h2>Talk to MR-365</h2>
        <div id="chat-box"></div>
        <input type="text" id="user-input" placeholder="Type your message..." onkeypress="handleKey(event)">

        <script>
            const chatBox = document.getElementById('chat-box');
            const input = document.getElementById('user-input');

            function appendMessage(message, sender) {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('message', sender);

                const avatar = document.createElement('div');
                avatar.classList.add('avatar');

                const bubble = document.createElement('div');
                bubble.classList.add('bubble');
                bubble.textContent = message;

                messageDiv.appendChild(sender === "user" ? bubble : avatar);
                messageDiv.appendChild(sender === "user" ? avatar : bubble);

                chatBox.appendChild(messageDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            function handleKey(event) {
                if (event.key === 'Enter') {
                    const message = input.value.trim();
                    if (!message) return;
                    appendMessage(message, "user");
                    input.value = "";

                    fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ message })
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.response) {
                            appendMessage(data.response, "bot");
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

# Health check
@app.route("/", methods=["GET"])
def index():
    return "<h3>MR-365 Chatbot is running.</h3>"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
