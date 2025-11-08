# app.py — Sobrio V2.7 (Flash + HARM + UX Polished)
# Full deployment-ready version with best-in-class UX and safety guardrails

from flask import Flask, request, jsonify, render_template_string, session
from flask_cors import CORS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
import os, re, uuid
from datetime import datetime

# --- Flask Setup ---
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-key")
CORS(app, origins=["https://myrecovery365.com"], supports_credentials=True)

# --- Model Setup ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=GEMINI_API_KEY,
    temperature=0.7
)

# --- Prompts ---
BASE_PROMPT = ChatPromptTemplate.from_template("""
You are Sobrio, a compassionate AI recovery companion who offers non‑judgmental,
evidence‑based guidance rooted in peer recovery and harm reduction.

Respond with:
- Empathy and encouragement
- Clean formatting with spacing and bullet points
- Clear line breaks and bold key terms
- Avoid filler phrases like "Okay, I understand" — go straight to helpful content.
- Include local or online recovery resources when appropriate.

Conversation so far:
{chat_history}

User context:
{user_context}

User message: {input}

Answer clearly and kindly.
""")

RELAPSE_PROMPT = ChatPromptTemplate.from_template("""
The user shows signs of relapse risk or cravings.

Be calm, supportive, and offer:
- Suggestions to cope
- Encouragement to contact support systems
- Helpful recovery tools

Conversation history:
{chat_history}
User message: {input}

Respond clearly, using bullets, line spacing, and bold key terms.
""")

CRISIS_KEYWORDS = [
    r"\b(kill myself|suicide|end my life|want to die|better off dead)\b",
    r"\b(overdose|od'ing|taking all|swallow all)\b",
    r"\b(can't go on|no reason to live)\b",
    r"\b(hurt myself|self harm|cut myself)\b"
]

RELAPSE_KEYWORDS = [
    r"\b(relapsed|used again|drank again|slipped up)\b",
    r"\b(bought|scored|dealer)\b",
    r"\b(craving|urge|trigger|tempt)\b"
]

HARM_CATEGORIES = {
    "H": ["violence", "abuse", "hurt", "harm", "threat", "danger"],
    "A": ["addiction", "craving", "drug", "alcohol", "relapse", "use"],
    "R": ["risky", "unsafe", "alone", "depressed", "hopeless"],
    "M": ["medication", "doctor", "treatment", "therapy", "diagnosis"]
}

def detect_harm_categories(text):
    text_lower = text.lower()
    return [k for k, words in HARM_CATEGORIES.items() if any(w in text_lower for w in words)]

def detect_crisis(msg):  return any(re.search(p, msg, re.I) for p in CRISIS_KEYWORDS)
def detect_relapse(msg): return any(re.search(p, msg, re.I) for p in RELAPSE_KEYWORDS)

def crisis_response():
    return """I hear that you’re in deep distress right now, and your life matters.

Please reach out immediately:
✎ **988 Suicide & Crisis Lifeline** (call or text)
💬 **Crisis Text Line** — Text HOME to 741741
🏥 **Emergency:** Call 911 or go to the nearest ER.

You are not alone. Help is available right now."""

# --- Memory Store ---
conversations = {}

def get_or_create_session():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_memory(session_id):
    if session_id not in conversations:
        conversations[session_id] = {
            'memory': ConversationBufferWindowMemory(k=5, return_messages=True),
            'user_data': {'count': 0, 'topics': [], 'created': datetime.now().isoformat()}
        }
    return conversations[session_id]

# --- Routes ---
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        msg = data.get("message", "").strip()
        if not msg:
            return jsonify({"error": "Message required"}), 400

        sid = get_or_create_session()
        conv = get_memory(sid)
        memory, user = conv['memory'], conv['user_data']
        user['count'] += 1

        if detect_crisis(msg):
            return jsonify({"response": crisis_response(), "crisis": True})

        relapse_flag = detect_relapse(msg)
        harm_flags = detect_harm_categories(msg)
        chat_history = memory.load_memory_variables({}).get("history", "")
        context = f"Messages: {user['count']}. Topics: {', '.join(user['topics'][-3:]) if user['topics'] else 'N/A'}"

        chain = LLMChain(llm=llm, prompt=RELAPSE_PROMPT if relapse_flag else BASE_PROMPT)
        response = chain.run({"input": msg, "chat_history": chat_history, "user_context": context})

        memory.save_context({"input": msg}, {"output": response})
        user['topics'].extend(harm_flags)

        return jsonify({"response": response, "harm_categories": harm_flags, "relapse": relapse_flag})
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal error. Please try again later."}), 500

@app.route("/chat-ui")
def chat_ui():
    return render_template_string(UI_HTML)

@app.route("/")
def root():
    return """<h3>✅ Sobrio V2.7 is running.</h3><p><a href='/chat-ui'>Launch Chat</a></p>"""

# --- Embedded UI with Clean UX ---
UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sobrio - Chat UI</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

    body {
      font-family: 'Inter', sans-serif;
      background: #f1f5f9;
      margin: 0;
      padding: 0;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
    }

    #chat-wrapper {
      background: white;
      border-radius: 16px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
      width: 100%;
      max-width: 480px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    header {
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: white;
      padding: 16px;
      text-align: center;
    }

    #chat-box {
      flex: 1;
      padding: 16px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .message {
      padding: 10px 14px;
      font-size: 0.95rem;
      max-width: 85%;
      border-radius: 16px;
      line-height: 1.4;
      white-space: pre-wrap;
      animation: fadeIn 0.3s ease;
    }

    .user {
      align-self: flex-end;
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: white;
      border-bottom-right-radius: 4px;
    }

    .bot {
      align-self: flex-start;
      background: #e5e5ea;
      color: #111;
      border-bottom-left-radius: 4px;
    }

    footer {
      display: flex;
      padding: 10px;
      border-top: 1px solid #eee;
      background: #f9fafb;
    }

    input {
      flex: 1;
      padding: 10px 14px;
      font-size: 0.95rem;
      border: 2px solid #ddd;
      border-radius: 20px;
      outline: none;
      transition: border-color 0.2s;
    }

    input:focus {
      border-color: #667eea;
    }

    button {
      padding: 10px 18px;
      margin-left: 10px;
      background: linear-gradient(135deg, #667eea, #764ba2);
      color: white;
      font-weight: 600;
      border: none;
      border-radius: 20px;
      cursor: pointer;
      transition: background 0.3s;
    }

    button:hover {
      opacity: 0.9;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>
  <div id="chat-wrapper">
    <header>
      <h2>👤 Sobrio</h2>
      <p>Your confidential recovery companion</p>
    </header>

    <div id="chat-box"></div>

    <footer>
      <input id="user-input" placeholder="Type your message..." />
      <button onclick="sendMessage()">Send</button>
    </footer>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script>
    const chatBox = document.getElementById('chat-box');
    const input = document.getElementById('user-input');

    function appendMarkdown(text, sender) {
      const div = document.createElement('div');
      div.className = 'message ' + sender;
      div.innerHTML = marked.parse(text);
      chatBox.appendChild(div);
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    function sendMessage() {
      const msg = input.value.trim();
      if (!msg) return;
      appendMarkdown(msg, 'user');
      input.value = '';

      fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ message: msg })
      })
        .then(r => r.json())
        .then(data => {
          if (data.response) {
            appendMarkdown(data.response, 'bot');
            if (data.harm_categories?.length) {
              appendMarkdown("\u26A0\uFE0F **HARM Alert**: " + data.harm_categories.join(', '), 'bot');
            }
          } else {
            appendMarkdown("*I'm having trouble responding.*", 'bot');
          }
        })
        .catch(() => appendMarkdown("*Network error.*", 'bot'));
    }

    input.addEventListener('keypress', e => {
      if (e.key === 'Enter') sendMessage();
    });

    window.onload = () => {
      setTimeout(() => appendMarkdown("\u{1F44B} **Hi, I'm Sobrio.** How can I support you today?", 'bot'), 300);
    };
  </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
