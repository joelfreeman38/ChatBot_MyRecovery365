# app.py

from flask import Flask, request, jsonify, render_template_string, session
from flask_cors import CORS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
import os
import re
from datetime import datetime
import json
import uuid

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-this")
CORS(app, origins=["https://myrecovery365.com"], supports_credentials=True)

# ✅ Supported real-time model
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key-here")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", google_api_key=GEMINI_API_KEY, temperature=0.7)

# --- Prompts ---
BASE_PROMPT = ChatPromptTemplate.from_template("""
You are Sobrio, a compassionate AI recovery coach trained in evidence-based addiction recovery approaches. You are NOT a therapist or doctor.

Use these principles:
- Reflective listening, validation, and empathy
- Motivational interviewing (OARS)
- Harm reduction and trauma-informed support
- Peer recovery and holistic wellness (mind, body, spirit)
- Avoid judgment, shame, or clinical language
- Emphasize small wins, progress, support systems

Chat History:
{chat_history}

User Context:
{user_context}

Current Message: {input}

Your response:
""")

RELAPSE_PROMPT = ChatPromptTemplate.from_template("""
The user may have relapsed or is at high risk. Be warm, non-judgmental, and supportive.

Conversation History: {chat_history}
Current Message: {input}

Your response:
- Validate their honesty
- Normalize relapse as part of some recovery journeys
- Ask what they need right now
- Encourage reaching out to human support (sponsor, group, therapist)
""")

# --- Crisis Keywords ---
CRISIS_KEYWORDS = [
    r'\b(kill myself|suicide|end my life|want to die|better off dead)\b',
    r'\b(overdose|od\'ing|taking all|swallow all)\b',
    r'\b(can\'t go on|no reason to live|no point living)\b',
    r'\b(hurt myself|self harm|cut myself)\b'
]

RELAPSE_KEYWORDS = [
    r'\b(relapsed|used again|drank again|slipped up)\b',
    r'\b(bought|scored|dealer|plug)\b',
    r'\b(craving|urge|trigger|tempt)\b'
]

# --- Conversation Store ---
conversations = {}

def get_or_create_session():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_conversation_memory(session_id):
    if session_id not in conversations:
        conversations[session_id] = {
            'memory': ConversationBufferWindowMemory(k=5, return_messages=True),
            'user_data': {
                'message_count': 0,
                'topics_discussed': [],
                'first_interaction': datetime.now().isoformat()
            }
        }
    return conversations[session_id]

def detect_crisis(message):
    for pattern in CRISIS_KEYWORDS:
        if re.search(pattern, message, re.IGNORECASE):
            return True
    return False

def detect_relapse(message):
    for pattern in RELAPSE_KEYWORDS:
        if re.search(pattern, message, re.IGNORECASE):
            return True
    return False

def get_crisis_response():
    return """I hear that you're in a really difficult place right now, and I want you to know that your life matters.

**Please reach out immediately:**
- 📞 **988 Suicide & Crisis Lifeline**: Call or text 988 (24/7)
- 📱 **Crisis Text Line**: Text HOME to 741741
- 🏥 **Emergency**: Visit your nearest ER or call 911

You're not alone. I'm here to support your recovery, but a trained crisis counselor can help you through this moment right now."""

def extract_topics(text):
    keywords = {
        'cravings': ['craving', 'urge'],
        'triggers': ['trigger', 'tempted'],
        'emotions': ['anxious', 'angry', 'depressed'],
        'support': ['sponsor', 'group', 'meeting', 'therapy'],
        'relapse': ['relapsed', 'drank', 'used'],
        'life stress': ['job', 'relationship', 'family']
    }
    found = []
    for topic, words in keywords.items():
        if any(w in text.lower() for w in words):
            found.append(topic)
    return found

def extract_user_context(user_data):
    if user_data['message_count'] == 0:
        return "First conversation."
    context = f"Message count: {user_data['message_count']}."
    if user_data['topics_discussed']:
        context += f" Topics: {', '.join(user_data['topics_discussed'][-3:])}."
    return context

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    session_id = get_or_create_session()
    conv = get_conversation_memory(session_id)
    memory = conv['memory']
    user_data = conv['user_data']
    user_data['message_count'] += 1

    if detect_crisis(user_input):
        return jsonify({
            "response": get_crisis_response(),
            "crisis_detected": True
        })

    relapse_flag = detect_relapse(user_input)
    chat_history = memory.load_memory_variables({}).get("history", "")
    user_context = extract_user_context(user_data)

    if relapse_flag:
        prompt = RELAPSE_PROMPT
    else:
        prompt = BASE_PROMPT

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run({
        "input": user_input,
        "chat_history": chat_history,
        "user_context": user_context
    })

    memory.save_context({"input": user_input}, {"output": response})
    user_data['topics_discussed'].extend(extract_topics(user_input))

    return jsonify({
        "response": response,
        "relapse_support": relapse_flag
    })

@app.route("/chat-ui", methods=["GET"])
def chat_ui():
    return render_template_string(EMBEDDED_UI)

@app.route("/", methods=["GET"])
def index():
    return "<h3>✅ Sobrio AI Recovery Chatbot is running.</h3><p><a href='/chat-ui'>Launch Chat UI</a></p>"

# --- Embedded UI Template ---
EMBEDDED_UI = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Sobrio - Recovery Chat</title>
  <style>
    body {
      background: linear-gradient(to right, #667eea, #764ba2);
      font-family: Arial, sans-serif;
      display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      padding: 20px; min-height: 100vh; color: white;
    }
    #chat-box {
      background: #fff; color: #333;
      width: 100%; max-width: 600px;
      height: 500px; overflow-y: auto;
      padding: 20px; border-radius: 12px;
      margin-bottom: 15px;
    }
    .message { margin: 12px 0; }
    .user { text-align: right; }
    .bot { text-align: left; }
    input[type="text"] {
      width: 80%; padding: 12px;
      border-radius: 8px; border: none;
    }
    button {
      padding: 12px 20px;
      background: #764ba2; border: none;
      color: white; border-radius: 8px;
      cursor: pointer;
    }
    .header { text-align: center; margin-bottom: 20px; }
    .header h1 { margin: 0; font-size: 2rem; }
  </style>
</head>
<body>
  <div class="header">
    <h1>🌱 Sobrio</h1>
    <p>Your confidential recovery companion</p>
  </div>
  <div id="chat-box"></div>
  <div>
    <input type="text" id="user-input" placeholder="Type your message...">
    <button onclick="sendMessage()">Send</button>
  </div>
  <script>
    const chatBox = document.getElementById('chat-box');
    const input = document.getElementById('user-input');

    function appendMessage(text, sender) {
      const div = document.createElement('div');
      div.className = 'message ' + sender;
      div.textContent = text;
      chatBox.appendChild(div);
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    function sendMessage() {
      const msg = input.value.trim();
      if (!msg) return;
      appendMessage(msg, 'user');
      input.value = '';

      fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ message: msg })
      })
      .then(res => res.json())
      .then(data => {
        if (data.response) appendMessage(data.response, 'bot');
        else appendMessage("I'm having trouble responding.", 'bot');
      })
      .catch(() => appendMessage("Connection error.", 'bot'));
    }

    input.addEventListener("keypress", (e) => {
      if (e.key === "Enter") sendMessage();
    });

    window.onload = () => {
      setTimeout(() => {
        appendMessage("Hi, I'm Sobrio. How can I support you today?", 'bot');
      }, 500);
    };
  </script>
</body>
</html>
"""
