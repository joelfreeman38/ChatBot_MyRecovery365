
# MR-365 Sober Coach API

This is a Flask-based API for the MR-365 AI Sober Coach chatbot, powered by Google's Gemini via LangChain.

## 🚀 Features

- AI responses trained on addiction recovery prompts
- Gemini 1.5 Flash integration
- REST API endpoint at `/chat`
- Ready to deploy on Render

## 🛠 Tech Stack

- Flask
- LangChain
- Gemini API
- Transformers
- Gunicorn (for production)

---

## 🔧 Local Setup

```bash
git clone https://github.com/yourusername/mr365-flask-api.git
cd mr365-flask-api
pip install -r requirements.txt
export GEMINI_API_KEY=your-api-key-here
python app.py
```

---

## 🌐 Deploying to Render

1. Create a free account at [Render](https://render.com)
2. Click **"New Web Service"**
3. Connect your GitHub repo
4. Use these settings:

- **Environment:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

5. Add environment variable:
```
GEMINI_API_KEY = your-api-key-here
```

6. Deploy and get your public endpoint URL!

---

## 🧠 Endpoint

**POST** `/chat`

**Request:**
```json
{
  "message": "How do I stay sober today?"
}
```

**Response:**
```json
{
  "response": "Take it one step at a time. Remember why you started your journey."
}
```

---

## 📄 License

MIT – for private use and client delivery only.
