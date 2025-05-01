from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('input', '').lower()

    relapse_triggers = ['i used', 'i relapsed', 'i drank', 'i slipped', 'i messed up']
    anxiety_triggers = ['overwhelmed', 'too much', "can't handle", 'panic', 'spiraling']
    suicidal_triggers = ['i want to die', 'i can’t do this', "i can't do this", 'i want to give up', 'i feel hopeless', 'i don’t want to live', "i don't want to live", 'i want to end it', "i'm suicidal", 'i feel like ending it']

    # Check for suicide risk first
    if any(phrase in user_input for phrase in suicidal_triggers):
        crisis_message = """I'm really sorry you're feeling this way. You're not alone — and there are people who care and want to help.

Call or text 988 (U.S. Suicide & Crisis Lifeline)
Call 1-833-456-4566 (Talk Suicide Canada)
Call 116 123 (Samaritans UK)
Call 13 11 14 (Lifeline Australia)
Call +91 9152987821 (iCall India)

These services are confidential and available 24/7. Please consider talking to someone — you are not alone."""
        return jsonify({"response": crisis_message})

    # Check for relapse
    if any(phrase in user_input for phrase in relapse_triggers):
        return jsonify({"response": "It’s okay to have setbacks — what matters is what you do next. You're not starting over; you're continuing your journey. Would you like to reflect on what happened or talk through your next step?"})

    # Check for anxiety/overwhelm
    if any(phrase in user_input for phrase in anxiety_triggers):
        return jsonify({"response": "It sounds like you're feeling overwhelmed. Let's take a breath together. You're not alone, and we can talk through what's weighing on you one step at a time."})

    # === Gemini Prompt and Response Section ===
    response_text = "This is a placeholder response from Sobrio."
    return jsonify({"response": response_text})

@app.route('/chat-ui')
def chat_ui():
    return '''
    <html>
    <head><title>Sobrio Chat</title></head>
    <body>
    <h1>Chat with Sobrio</h1>
    <form id="chat-form">
        <input type="text" id="user-input" placeholder="Type your message..." />
        <button type="submit">Send</button>
    </form>
    <div id="chat-response"></div>
    <script>
    document.getElementById('chat-form').onsubmit = async function(e) {
        e.preventDefault();
        const input = document.getElementById('user-input').value;
        const res = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ input })
        });
        const data = await res.json();
        document.getElementById('chat-response').innerText = data.response;
    };
    </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)