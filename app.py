# app.py — Sobrio V2.6 Flash + HARM Category Detection
# Production‑ready Flask app for Render / WordPress integration

from flask import Flask, request, jsonify, render_template_string, session
from flask_cors import CORS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
import os, re, uuid, json
from datetime import datetime

# --- Flask Setup ---
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "replace-with-a-secure-key")
CORS(app, origins=["https://myrecovery365.com"], supports_credentials=True)

# --- Model Setup ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key-here")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-exp",
    google_api_key=GEMINI_API_KEY,
    temperature=0.7
)

# --- Prompts ---
BASE_PROMPT = ChatPromptTemplate.from_template("""
You are Sobrio, a compassionate AI recovery companion who offers non‑judgmental,
evidence‑based guidance rooted in peer recovery, harm‑reduction, and motivational interviewing.
Do not act as a therapist or medical professional.

Principles:
- Reflective listening, empathy, validation.
- Use open questions (OARS).
- Encourage self‑awareness and support networks.
- Avoid judgment or prescriptive advice.

Conversation so far:
{chat_history}

User context:
{user_context}

User message: {input}

Respond with anwering users questions clearly and accurately.
""")

RELAPSE_PROMPT = ChatPromptTemplate.from_template("""
The user shows signs of relapse risk or cravings.
Be calm, non‑judgmental, and supportive.

Conversation history:
{chat_history}

User message: {input}

Response goals:
- Validate honesty and courage.
- Explore what led up to this moment.
- Encourage next steps (contact sponsor, meeting, coping tools).
- Avoid shame. Offer connection.
- If the user is in emotional distress, offer empathy **after** answering the question.
- Avoid excessive praise or vague encouragement unless the user is in crisis.
- Keep responses concise, helpful, and grounded in addiction recovery principles.
""")

# --- Keyword Detection ---
CRISIS_KEYWORDS = [
    r'\b(kill myself|suicide|end my life|want to die|better off dead)\b',
    r'\b(overdose|od\'ing|taking all|swallow all)\b',
    r'\b(can\'t go on|no reason to live)\b',
    r'\b(hurt myself|self harm|cut myself)\b'
]

RELAPSE_KEYWORDS = [
    r'\b(relapsed|used again|drank again|slipped up)\b',
    r'\b(bought|scored|dealer)\b',
    r'\b(craving|urge|trigger|tempt)\b'
]

# --- HARM Category Detection ---
HARM_CATEGORIES = {
    "H": ["violence", "abuse", "hurt", "harm", "threat", "danger"],
    "A": ["addiction", "craving", "drug", "alcohol", "relapse", "use"],
    "R": ["risky", "unsafe", "alone", "depressed", "hopeless"],
    "M": ["medication", "doctor", "treatment", "therapy", "diagnosis"]
}

def detect_harm_categories(text):
    text_lower = text.lower()
    detected = [k for k, words in HARM_CATEGORIES.items() if any(w in text_lower for w in words)]
    return detected

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

# --- Detection Functions ---
def detect_crisis(msg):  return any(re.search(p, msg, re.I) for p in CRISIS_KEYWORDS)
def detect_relapse(msg): return any(re.search(p, msg, re.I) for p in RELAPSE_KEYWORDS)

def crisis_response():
    return """I hear that you’re in deep distress right now, and your life matters.

Please reach out immediately:
📞 **988 Suicide & Crisis Lifeline** (call or text)
💬 **Crisis Text Line** — Text HOME to 741741
🏥 **Emergency:** Call 911 or go to the nearest ER.

You are not alone. Help is available right now."""

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
        context = f"Messages so far: {user['count']}. Topics: {', '.join(user['topics'][-3:]) if user['topics'] else 'N/A'}"

        chain = LLMChain(llm=llm, prompt=RELAPSE_PROMPT if relapse_flag else BASE_PROMPT)
        response = chain.run({"input": msg, "chat_history": chat_history, "user_context": context})

        memory.save_context({"input": msg}, {"output": response})
        user['topics'].extend(harm_flags)

        return jsonify({
            "response": response,
            "harm_categories": harm_flags,
            "relapse": relapse_flag
        })
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal error. Please try again later."}), 500

@app.route("/chat-ui", methods=["GET"])
def chat_ui():
    return render_template_string(UI_HTML)

@app.route("/", methods=["GET"])
def home():
    return "<h3>✅ Sobrio AI Chatbot v2.6 is running.</h3><p><a href='/chat-ui'>Open Chat UI</a></p>"

# --- Embedded UI ---
UI_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<title>Sobrio - Recovery Chat</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
body {
  font-family: 'Inter', sans-serif;
  background: #f1f5f9;
  margin: 0; padding: 20px;
  display: flex; justify-content: center; align-items: center;
  min-height: 100vh;
}
#chat-wrapper {
  background: #fff; border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
  width: 100%; max-width: 700px;
  display: flex; flex-direction: column;
  overflow: hidden;
}
header {
  background: linear-gradient(135deg,#667eea,#764ba2);
  color: white; padding: 20px; text-align: center;
}
header h1 { margin: 0; font-weight: 600; }
#chat-box {
  flex: 1; padding: 20px; overflow-y: auto;
  display: flex; flex-direction: column;
}
.message {
  max-width: 70%; margin: 10px 0; padding: 12px 18px;
  border-radius: 20px; line-height: 1.4;
  animation: fadeIn .3s ease;
}
@keyframes fadeIn { from{opacity:0;transform:translateY(8px);} to{opacity:1;transform:translateY(0);} }
.user { align-self: flex-end; background: linear-gradient(135deg,#667eea,#764ba2); color: #fff; border-bottom-right-radius: 4px; }
.bot  { align-self: flex-start; background: #e5e5ea; color: #000; border-bottom-left-radius: 4px; }
footer {
  display: flex; padding: 15px; border-top: 1px solid #eee;
}
input {
  flex: 1; padding: 12px; border: 2px solid #ddd;
  border-radius: 24px; font-size: 1rem; outline: none;
}
input:focus { border-color: #667eea; }
button {
  background: linear-gradient(135deg,#667eea,#764ba2);
  color: white; border: none; border-radius: 24px;
  padding: 12px 24px; margin-left: 10px;
  cursor: pointer; font-weight: 600;
}
button:hover { opacity: 0.9; }
</style>
</head>
<body>
<div id="chat-wrapper">
  <header><h1>🌱 Sobrio</h1><p>Your confidential recovery companion</p></header>
  <div id="chat-box"></div>
  <footer>
    <input id="user-input" placeholder="Type your message..." />
    <button onclick="sendMessage()">Send</button>
  </footer>
</div>
<script>
const chatBox=document.getElementById('chat-box');
const input=document.getElementById('user-input');
function append(text,sender){
  const d=document.createElement('div');
  d.className='message '+sender; d.textContent=text;
  chatBox.appendChild(d); chatBox.scrollTop=chatBox.scrollHeight;
}
function sendMessage(){
  const msg=input.value.trim(); if(!msg)return;
  append(msg,'user'); input.value='';
  fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},
  credentials:'include',body:JSON.stringify({message:msg})})
  .then(r=>r.json()).then(data=>{
    if(data.response){append(data.response,'bot');
      if(data.harm_categories?.length)
        append("⚠️ HARM flags detected: "+data.harm_categories.join(', '),'bot');
    } else append("I'm having trouble responding.","bot");
  }).catch(()=>append("Network error.","bot"));
}
input.addEventListener('keypress',e=>{if(e.key==='Enter')sendMessage();});
window.onload=()=>setTimeout(()=>append("Hi, I'm Sobrio. How can I support you today?","bot"),500);
</script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
