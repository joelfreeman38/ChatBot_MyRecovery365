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

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key-here")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", google_api_key=GEMINI_API_KEY, temperature=0.7)

# Crisis keywords and patterns
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

# Enhanced prompt with recovery-specific guidance
ENHANCED_PROMPT = ChatPromptTemplate.from_template("""
You are Sobrio, a certified AI recovery specialist trained in evidence-based recovery practices.

CREDENTIALS & TRAINING:
- CCAR (Connecticut Community for Addiction Recovery) Certified Recovery Coach
- MCBAP (Massachusetts Certified Board of Addiction Professionals) Certified
- Specialized training in peer recovery support, motivational interviewing, and trauma-informed care
- Deep understanding of 12-Step, SMART Recovery, Recovery Dharma, and harm reduction approaches

CORE RECOVERY PRINCIPLES:
- Use motivational interviewing: Open questions, affirmations, reflective listening, summaries (OARS)
- Person-centered: Recovery is self-directed and individualized
- Trauma-informed: Recognize that many in recovery have experienced trauma
- Emphasize autonomy: The person is the expert on their own life
- Meet them where they are: No judgment about stages of change (pre-contemplation, contemplation, preparation, action, maintenance)
- Celebrate small wins: Recovery is built on incremental progress
- Holistic approach: Address mind, body, spirit, and community
- Hope-based: Recovery is possible and happening every day

RECOVERY COACH APPROACH:
1. **Active Listening**: Truly hear what they're saying AND not saying
2. **Empowerment**: Help them discover their own solutions and strengths
3. **Identify Strengths**: Recognize and build on what's already working
4. **Explore Values**: Connect recovery goals to their deeper values and purpose
5. **WRAP (Wellness Recovery Action Plan)**: Help identify triggers, early warning signs, and action plans
6. **Support Network**: Encourage building connections (sponsor, support group, sober friends)
7. **Self-Care**: Address physical, emotional, mental, and spiritual wellness
8. **Relapse as Learning**: If relapse occurs, explore it without shame - what happened, what can be learned?

CONVERSATION HISTORY:
{chat_history}

CURRENT USER STATE (if available):
{user_context}

GUIDELINES FOR THIS CONVERSATION:
1. Acknowledge their courage and honesty in sharing
2. Use reflective listening - mirror back feelings and content you hear
3. Ask open-ended questions about their experience (not just facts)
4. Explore ambivalence with compassion - it's normal to have mixed feelings
5. Connect to their "why" - their reasons, values, and goals for recovery
6. Offer evidence-based coping strategies when appropriate (not prescriptive advice)
7. Remind them: You're a trained recovery coach, but not a replacement for therapists, medical professionals, or sponsors
8. Use recovery language: "person in recovery" not "addict", "substance use disorder" not "junkie"

SPECIFIC RECOVERY COACHING TECHNIQUES:
- **Scaling Questions**: "On a scale of 1-10, how confident are you in staying sober this week?"
- **Exception Questions**: "Tell me about a time when you successfully handled a craving"
- **Miracle Question**: "If you woke up tomorrow and your recovery was exactly where you wanted it, what would be different?"
- **Values Exploration**: "What matters most to you? How does your recovery support that?"
- **HALT Check**: If sensing struggle, ask "Are you Hungry, Angry, Lonely, or Tired right now?"

AVOID:
- Giving direct advice unless specifically asked
- Being preachy, prescriptive, or one-size-fits-all
- Shame, judgment, or "should" language
- Medical diagnoses or medication recommendations
- Overly clinical terminology that creates distance
- Repetitive phrases - vary your language naturally
- Assuming what type of recovery path they follow (they may not be 12-Step)

RESPONSE STRUCTURE (Natural Conversation Flow):
- Brief empathic reflection that validates their experience (1-2 sentences)
- Deeper exploration, connection to values, or gentle observation (2-3 sentences)  
- Open-ended question that invites them to go deeper or explore next steps

Remember: You're walking alongside them, not leading them. They're the expert on their life.

User's message: {input}

Sobrio:
""")

# Store conversations in memory (in production, use database)
conversations = {}

def get_or_create_session():
    """Get or create session ID for user"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_conversation_memory(session_id):
    """Get or create conversation memory for session"""
    if session_id not in conversations:
        conversations[session_id] = {
            'memory': ConversationBufferWindowMemory(k=5, return_messages=True),
            'user_data': {
                'first_interaction': datetime.now().isoformat(),
                'message_count': 0,
                'topics_discussed': [],
                'mood_indicators': []
            }
        }
    return conversations[session_id]

def detect_crisis(message):
    """Detect crisis language in user message"""
    message_lower = message.lower()
    for pattern in CRISIS_KEYWORDS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return True
    return False

def detect_relapse_risk(message):
    """Detect relapse indicators"""
    message_lower = message.lower()
    for pattern in RELAPSE_KEYWORDS:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return True
    return False

def get_crisis_response():
    """Return crisis response with resources"""
    return """I hear that you're in a really difficult place right now, and I want you to know that your life matters. What you're feeling is real and serious.

**Please reach out for immediate support:**

🆘 **988 Suicide & Crisis Lifeline**: Call or text 988 (24/7)
🆘 **Crisis Text Line**: Text HOME to 741741
🆘 **SAMHSA National Helpline**: 1-800-662-HELP (4357)
🆘 **Emergency**: Call 911 or go to your nearest emergency room

I'm here to listen, but I'm not equipped to provide the urgent care you need right now. A trained crisis counselor can give you the immediate support you deserve.

Would you be willing to reach out to one of these resources? I'll be here when you're ready to talk."""

def get_relapse_response(user_message, conversation_history):
    """Enhanced response for relapse situations"""
    relapse_prompt = f"""The user has indicated they may have relapsed or are at high risk. 

Previous conversation: {conversation_history}
Current message: {user_message}

Respond with:
1. No judgment - relapse is part of many recovery journeys
2. Validate their honesty in sharing
3. Ask what happened leading up to this moment
4. Explore what they need right now
5. Remind them: This doesn't erase their progress
6. Suggest reaching out to their support network/sponsor

Be warm, non-judgmental, and focused on moving forward."""
    
    return LLMChain(llm=llm, prompt=ChatPromptTemplate.from_template(relapse_prompt))

def extract_user_context(user_data):
    """Create context summary from user data"""
    if user_data['message_count'] == 0:
        return "First conversation with this user."
    
    context = f"Message #{user_data['message_count']}. "
    if user_data['topics_discussed']:
        context += f"Previous topics: {', '.join(user_data['topics_discussed'][-3:])}. "
    return context

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("message", "").strip()

        if not user_input:
            return jsonify({"error": "No input message provided."}), 400

        # Get or create session
        session_id = get_or_create_session()
        conv_data = get_conversation_memory(session_id)
        memory = conv_data['memory']
        user_data = conv_data['user_data']

        # Update user data
        user_data['message_count'] += 1

        # Crisis detection
        if detect_crisis(user_input):
            response = get_crisis_response()
            return jsonify({
                "response": response,
                "crisis_detected": True,
                "show_resources": True
            })

        # Relapse detection
        is_relapse_risk = detect_relapse_risk(user_input)

        # Build context
        chat_history = memory.load_memory_variables({}).get('history', '')
        user_context = extract_user_context(user_data)

        # Generate response
        if is_relapse_risk:
            chain = get_relapse_response(user_input, chat_history)
            response = chain.run({"input": user_input})
        else:
            chain = LLMChain(llm=llm, prompt=ENHANCED_PROMPT)
            response = chain.run({
                "input": user_input,
                "chat_history": chat_history,
                "user_context": user_context
            })

        # Save to memory
        memory.save_context({"input": user_input}, {"output": response})

        # Extract topics (simple keyword extraction)
        topics = extract_topics(user_input)
        user_data['topics_discussed'].extend(topics)

        return jsonify({
            "response": response,
            "session_id": session_id,
            "relapse_support": is_relapse_risk
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "I'm having trouble responding right now. Please try again."}), 500

def extract_topics(text):
    """Simple topic extraction"""
    recovery_topics = {
        'cravings': ['craving', 'urge', 'want to use'],
        'triggers': ['trigger', 'temptation', 'reminded'],
        'emotions': ['angry', 'sad', 'anxious', 'depressed', 'lonely'],
        'relationships': ['family', 'friend', 'partner', 'spouse'],
        'meetings': ['meeting', 'group', 'aa', 'na', 'sponsor'],
        'work': ['job', 'work', 'career', 'employment'],
        'progress': ['sober', 'clean', 'days', 'months', 'years']
    }
    
    found_topics = []
    text_lower = text.lower()
    for topic, keywords in recovery_topics.items():
        if any(kw in text_lower for kw in keywords):
            found_topics.append(topic)
    return found_topics

@app.route("/clear-session", methods=["POST"])
def clear_session():
    """Allow users to start fresh conversation"""
    session_id = session.get('session_id')
    if session_id and session_id in conversations:
        del conversations[session_id]
    session.clear()
    return jsonify({"message": "Session cleared"})

@app.route("/feedback", methods=["POST"])
def submit_feedback():
    """Collect beta tester feedback"""
    try:
        data = request.get_json()
        session_id = session.get('session_id', 'unknown')
        
        feedback = {
            'session_id': session_id,
            'rating': data.get('rating'),
            'helpful': data.get('helpful'),
            'comments': data.get('comments'),
            'timestamp': datetime.now().isoformat(),
            'felt_heard': data.get('felt_heard'),
            'would_use_again': data.get('would_use_again')
        }
        
        # In production, save to database
        # For now, log to file
        with open('beta_feedback.json', 'a') as f:
            f.write(json.dumps(feedback) + '\n')
        
        return jsonify({"message": "Thank you for your feedback!", "success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analytics", methods=["GET"])
def get_analytics():
    """Basic analytics for beta testing review"""
    try:
        total_sessions = len(conversations)
        total_messages = sum(conv['user_data']['message_count'] for conv in conversations.values())
        
        # Topic distribution
        all_topics = []
        for conv in conversations.values():
            all_topics.extend(conv['user_data']['topics_discussed'])
        
        from collections import Counter
        topic_counts = Counter(all_topics)
        
        return jsonify({
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "avg_messages_per_session": total_messages / max(total_sessions, 1),
            "top_topics": dict(topic_counts.most_common(10)),
            "active_sessions": len([c for c in conversations.values() if c['user_data']['message_count'] > 0])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/resources", methods=["GET"])
def resources():
    """Return recovery resources"""
    return jsonify({
        "crisis": {
            "988": "Suicide & Crisis Lifeline - Call or text 988",
            "samhsa": "1-800-662-HELP (4357) - SAMHSA National Helpline",
            "crisis_text": "Text HOME to 741741"
        },
        "recovery": {
            "aa": "https://www.aa.org/find-aa",
            "na": "https://www.na.org/meetingsearch/",
            "smart": "https://www.smartrecovery.org/",
            "celebrate_recovery": "https://www.celebraterecovery.com/"
        },
        "support": {
            "samhsa_treatment": "https://findtreatment.gov/",
            "recovery_dharma": "https://recoverydharma.org/"
        }
    })

@app.route("/chat-ui", methods=["GET"])
def chat_ui():
    return render_template_string(ENHANCED_UI_TEMPLATE)

# Enhanced UI with better UX
ENHANCED_UI_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Sobrio - Your Recovery Companion</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }
        .header {
            color: white;
            text-align: center;
            margin-bottom: 20px;
        }
        .header h1 { font-size: 2rem; font-weight: 600; margin-bottom: 5px; }
        .credentials { 
            font-size: 0.85rem; 
            opacity: 0.95; 
            font-weight: 500;
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 8px;
        }
        .header p { opacity: 0.9; margin-top: 8px; }
        .disclaimer {
            background: rgba(255, 255, 255, 0.15);
            color: white;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-size: 0.9rem;
            max-width: 700px;
            text-align: center;
        }
        #chat-container {
            width: 100%;
            max-width: 700px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            height: 600px;
        }
        #chat-box {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        .message {
            display: flex;
            margin-bottom: 16px;
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble {
            max-width: 75%;
            padding: 14px 18px;
            border-radius: 18px;
            font-size: 1rem;
            line-height: 1.5;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .user .bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }
        .bot .bubble {
            background: #f0f0f0;
            color: #333;
            border-bottom-left-radius: 4px;
        }
        .crisis-alert {
            background: #fee;
            border: 2px solid #c33;
            color: #c33;
            font-weight: 600;
        }
        .input-area {
            padding: 20px;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }
        #user-input {
            flex: 1;
            padding: 14px;
            font-size: 1rem;
            border: 2px solid #e0e0e0;
            border-radius: 24px;
            outline: none;
        }
        #user-input:focus {
            border-color: #667eea;
        }
        button {
            padding: 14px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 24px;
            cursor: pointer;
            font-weight: 600;
        }
        button:hover { opacity: 0.9; }
        .typing {
            display: none;
            padding: 10px;
            color: #999;
            font-style: italic;
        }
        .resources-link {
            text-align: center;
            padding: 10px;
            color: white;
            font-size: 0.9rem;
        }
        .resources-link a {
            color: white;
            text-decoration: underline;
        }
        .feedback-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #28a745;
            padding: 12px 20px;
            border-radius: 30px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 1000;
        }
        .feedback-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 2000;
            align-items: center;
            justify-content: center;
        }
        .feedback-content {
            background: white;
            padding: 30px;
            border-radius: 16px;
            max-width: 500px;
            width: 90%;
            color: #333;
        }
        .feedback-content h3 {
            margin-bottom: 20px;
            color: #667eea;
        }
        .feedback-content label {
            display: block;
            margin: 15px 0 5px;
            font-weight: 600;
        }
        .feedback-content input,
        .feedback-content textarea,
        .feedback-content select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 1rem;
        }
        .feedback-content textarea {
            min-height: 100px;
            resize: vertical;
        }
        .feedback-actions {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .feedback-actions button {
            flex: 1;
        }
        .close-btn {
            background: #6c757d;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🌱 Sobrio</h1>
        <div class="credentials">CCAR & MCBAP Certified Recovery Coach</div>
        <p>Your 24/7 Recovery Companion</p>
    </div>
    
    <div class="disclaimer">
        ⚠️ Sobrio is a CCAR & MCBAP certified AI recovery coach trained in evidence-based recovery practices. This is a supportive tool, not a replacement for professional therapy, medical advice, or human connection. In crisis? Call 988.
    </div>

    <div id="chat-container">
        <div id="chat-box"></div>
        <div class="typing" id="typing">Sobrio is typing...</div>
        <div class="input-area">
            <input type="text" id="user-input" placeholder="Share what's on your mind..." />
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <div class="resources-link">
        <a href="/resources" target="_blank">📚 Recovery Resources</a>
    </div>

    <script>
        const chatBox = document.getElementById('chat-box');
        const input = document.getElementById('user-input');
        const typing = document.getElementById('typing');

        function appendMessage(message, sender, isCrisis = false) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', sender);
            const bubble = document.createElement('div');
            bubble.classList.add('bubble');
            if (isCrisis) bubble.classList.add('crisis-alert');
            bubble.textContent = message;
            messageDiv.appendChild(bubble);
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function sendMessage() {
            const message = input.value.trim();
            if (!message) return;
            
            appendMessage(message, "user");
            input.value = "";
            typing.style.display = 'block';
            
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ message })
            })
            .then(res => res.json())
            .then(data => {
                typing.style.display = 'none';
                if (data.response) {
                    appendMessage(data.response, "bot", data.crisis_detected || false);
                } else {
                    appendMessage("I'm having trouble right now. Please try again.", "bot");
                }
            })
            .catch(err => {
                typing.style.display = 'none';
                appendMessage("Connection error. Please check your internet.", "bot");
            });
        }

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        // Welcome message
        window.onload = () => {
            setTimeout(() => {
                appendMessage("Hi, I'm Sobrio. I'm here to listen and support you on your recovery journey. What brings you here today?", "bot");
            }, 500);
        };
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return "<h3>✅ Sobrio Recovery Chatbot v2.5 is running.</h3><p><a href='/chat-ui'>Open Chat Interface</a></p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
