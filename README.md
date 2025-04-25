
# MR-365 AI Sober Coach 🤖💬

![MR-365 AI Chatbot](./mr365-chatbot.png)

[![GitHub](https://img.shields.io/badge/GitHub-Repo-blue?logo=github)](https://github.com/your-username/your-repo-name)
![Version](https://img.shields.io/badge/version-1.0.0-brightgreen)

**MR-365** is an AI-powered sober coaching chatbot designed to support individuals recovering from addiction.  
Built with empathy, privacy, and real-time interaction in mind.  
🔗 Live Site: [myrecovery365.com](https://myrecovery365.com)

---

## 📚 Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Technology Stack](#technology-stack)
- [Project Status](#project-status)
- [Contact](#contact)

---

## ✨ Features
- Real-time conversation with Gemini-powered AI
- Supportive and non-judgmental tone for addiction recovery
- Styled message bubbles with avatars
- Responsive design for mobile and desktop
- Easy integration into websites via iframe
- Secure backend with CORS protection
- WordPress-compatible embed setup

---

## 🛠 Installation

```bash
# Clone the repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

---

## 🚀 Usage

- Backend `/chat` route handles incoming POST messages.
- Frontend `/chat-ui` provides a styled web-based chat interface.
- Embed the chat UI into your site using an iframe:
  
```html
<iframe src="https://your-production-host/chat-ui" width="100%" height="600px" style="border: none;"></iframe>
```

---

## 🧰 Technology Stack

### 🖥️ Frontend
- **HTML5 + CSS3**: UI structure and styling
- **Vanilla JavaScript**: Handles message input, API requests, and dynamic message rendering
- **Responsive Design**: Mobile-friendly layout using flexbox
- **Avatars and bubble UI**: Chat interface with custom avatars and styled message bubbles
- **Embedded via iframe**: Seamless integration into WordPress or any static site

### ⚙️ Backend
- **Python 3.x**
- **Flask**: Lightweight REST API framework to serve endpoints
- **Flask-CORS**: Secure cross-origin requests between WordPress frontend and Flask backend

### 🧠 AI & Language Model
- **Google Gemini 1.5 Flash**: Advanced conversational AI via LangChain integration
- **LangChain**: Orchestrates prompt templates and model interaction
- **Custom prompt tuning**: Defines MR-365’s supportive tone and behavior

### ☁️ Deployment & DevOps
- **GitHub**: Source control and version management
- **Render**: Cloud deployment of the Flask API and chatbot interface
- **Environment Variables**: Secures Gemini API keys in deployment

### 🌐 CMS / Integration
- **WordPress + Elementor**: Powers the main site (myrecovery365.com)
- **WP HTML Embed**: Chatbot widget integrated via Elementor HTML block
- **WP Fusion + ActiveCampaign**: User automation and email workflow (mentioned in project context)

---

## 🚧 Project Status
**Current Version:** Stable and deployed  
**In Progress:**
- Typing animation
- Auto-scroll and UX polish
- Voice input (planned)

---

## 👤 Contact

**Joel Freeman**  
🔗 [myrecovery365.com](https://myrecovery365.com)
