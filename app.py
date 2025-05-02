from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_community.chat_models import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os

app = Flask(__name__)
CORS(app)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.7)

prompt_template = PromptTemplate(
    input_variables=["input"],
    template="""
You are Sobrio, a compassionate and encouraging sobriety support coach trained in addiction recovery and emotional support. Use warm, conversational, and non-judgmental language to respond to people seeking help. End each response with an open-ended question to keep the conversation going.

If a user expresses a relapse, depression, anxiety, or thoughts of self-harm, offer supportive resources and encourage them to seek real help. If someone is in crisis, prioritize empathy and point them to immediate support like 988 or international hotlines.

User: {input}
Sobrio:
"""
)

chain = LLMChain(llm=llm, prompt=prompt_template)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("input", "")
    user_input_lower = user_input.lower()

    relapse_triggers = ["i used", "i relapsed", "i drank", "i slipped", "i messed up"]
    anxiety_triggers = ["overwhelmed", "too much", "can't handle", "panic", "spiraling"]
    suicidal_triggers = [
        "i want to die", "i can’t do this", "i can't do this", "i want to give up",
        "i feel hopeless", "i don’t want to live", "i don't want to live",
        "i want to end it", "i'm suicidal", "i feel like ending it"
    ]

    if any(phrase in user_input_lower for phrase in suicidal_triggers):
        crisis_message = (
            "I'm really sorry you're feeling this way. You're not alone — and there are people who care and want to help.\n\n"
            "• Call or text 988 (U.S. Suicide & Crisis Lifeline)\n"
            "• Call 1-833-456-4566 (Talk Suicide Canada)\n"
            "• Call 116 123 (Samaritans UK)\n"
            "• Call 13 11 14 (Lifeline Australia)\n"
            "• Call +91 9152987821 (iCall India)\n\n"
            "These services are confidential and available 24/7. Please consider talking to someone — you are not alone."
        )
        return jsonify({"response": crisis_message})

    if any(phrase in user_input_lower for phrase in relapse_triggers):
        relapse_message = (
            "It’s okay to have setbacks — what matters is what you do next. "
            "You're not starting over; you're continuing your journey. Would you like to reflect on what happened or talk through your next step?"
        )
        return jsonify({"response": relapse_message})

    if any(phrase in user_input_lower for phrase in anxiety_triggers):
        anxiety_message = (
            "It sounds like you're feeling overwhelmed. Let's take a breath together. "
            "You're not alone, and we can talk through what's weighing on you one step at a time."
        )
        return jsonify({"response": anxiety_message})

    try:
        response = chain.run({"input": user_input})
    except Exception:
        response = "I'm having trouble generating a response right now, but I'm still here for you."

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)