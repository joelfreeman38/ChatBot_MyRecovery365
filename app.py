from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('input', '')

    
# Crisis Detection Block
user_input_lower = user_input.lower()
crisis_triggers = ['i want to die', 'i can’t do this', "i can't do this", 'i want to give up', 'i feel hopeless', 'i don’t want to live', "i don't want to live", 'i want to end it', "i'm suicidal", 'i feel like ending it']
if any(phrase in user_input_lower for phrase in crisis_triggers):
    return jsonify({"response": """I'm really sorry you're feeling this way. You're not alone — and there are people who care and want to help.

If you're in immediate danger or feel unsafe, please consider reaching out to a mental health professional or crisis line. You can call or text 988 in the U.S. anytime for free, confidential support."""}})


    # === Gemini Prompt and Response Section ===
    # Placeholder for Gemini API logic
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