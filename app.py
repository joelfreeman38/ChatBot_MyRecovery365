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
You are Sobrio, a recovery coach who is calm, emotionally intelligent, and deeply supportive. 
Speak like a human being sitting across from someone in recovery who’s opening up to you.

Follow this structure:

1. Start with a varied, natural tone of acknowledgment based on the user’s message. 
   Use different ways to express empathy — avoid repeating phrases like "Glad you reached out".

2. Share 2–3 gentle, supportive reflections or suggestions. Avoid long lists or mechanical tone.
   Sound conversational, not like a worksheet.

3. End with an open-ended, soft question like:
   - “What’s weighing on you most right now?”
   - “Want to talk about how that’s been affecting you?”
   - “Where should we start today?”

Avoid:
- Repetition of phrasing from past answers
- Robotic greetings
- Overly casual language like “Hey there”
- Homework-style checklists

Be a caring human voice. Slow, thoughtful, and present.

User: {input}
Sobrio:
""")

chain = LLMChain(llm=llm, prompt=prompt)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return jsonify({"error": "No input message provided."}), 400

    try:
        
    # Crisis Detection Block
    user_input_lower = user_input.lower()
    relapse_triggers = ["i used", "i relapsed", "i drank", "i slipped", "i messed up"]
    anxiety_triggers = ["overwhelmed", "too much", "can't handle", "panic", "spiraling"]
    suicidal_triggers = [
        "i want to die", "i can’t do this", "i can't do this", "i want to give up",
        "i feel hopeless", "i don’t want to live", "i don't want to live",
        "i want to end it", "i'm suicidal", "i feel like ending it"
    ]

    if any(phrase in user_input_lower for phrase in suicidal_triggers):
        crisis_message = """I'm really sorry you're feeling this way. You're not alone — and there are people who care and want to help.

• Call or text 988 (U.S. Suicide & Crisis Lifeline)
• Call 1-833-456-4566 (Talk Suicide Canada)
• Call 116 123 (Samaritans UK)
• Call 13 11 14 (Lifeline Australia)
• Call +91 9152987821 (iCall India)

These services are confidential and available 24/7. Please consider talking to someone — you are not alone."""
        return jsonify({{"response": crisis_message}})

    if any(phrase in user_input_lower for phrase in relapse_triggers):
        relapse_message = "It’s okay to have setbacks — what matters is what you do next. You're not starting over; you're continuing your journey. Would you like to reflect on what happened or talk through your next step?"
        return jsonify({{"response": relapse_message}})

    if any(phrase in user_input_lower for phrase in anxiety_triggers):
        anxiety_message = "It sounds like you're feeling overwhelmed. Let's take a breath together. You're not alone, and we can talk through what's weighing on you one step at a time."
        return jsonify({{"response": anxiety_message}})


    try:
        response = chain.run({"input": user_input})
    except Exception as e:
        response = "I'm having trouble generating a response right now, but I'm still here for you."
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat-ui", methods=["GET"])
def chat_ui():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Let’s Talk – One Step at a Time</title>
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
                white-space: pre-wrap;
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
        <h2>Let’s Talk – One Step at a Time</h2>
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

@app.route("/", methods=["GET"])
def index():
    return "<h3>Sobrio Chatbot is running.</h3>"