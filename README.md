# 🤖 Sobrio: AI Recovery Coach

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](#)  
[![Build](https://img.shields.io/badge/deploy-render-green.svg)](https://myrecovery365.com/elementor-page-779/)  
[![Powered By](https://img.shields.io/badge/powered%20by-Gemini%202.5-blueviolet)](#)

---

## 🧭 Table of Contents
- [Project Overview](#project-overview)
- [Live Demo](#live-demo)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup & Deployment](#setup--deployment)
- [Sobrio’s Voice](#sobrios-voice)
- [Roadmap](#roadmap-v2)
- [Credits](#credits)
- [License](#license)

---

## 🔍 Project Overview

**Sobrio** is a purpose-driven, emotionally intelligent AI recovery companion.  
Version 2.0 builds on the initial foundation to deliver a deeper, more intuitive user experience — moving Sobrio closer to feeling like a real 24/7 recovery coach.

This version runs on a scalable Flask + Gemini backend, fully integrated into a WordPress/BuddyBoss membership environment, making it ready to evolve into a truly personalized mobile-friendly recovery app.

### 🌟 Vision:
Sobrio will evolve into a fully integrated wellness companion, embedded within:
- Secure member dashboards
- Personalized recovery journeys
- Journal and tracker access
- Real-time messaging and support escalation
- App-like experience via mobile PWA

Visit the current live integration:  
🔗 [https://myrecovery365.com/elementor-page-779/](https://myrecovery365.com/elementor-page-779/)

---

## 🚀 Live Demo

> [View Sobrio on MyRecovery365](https://myrecovery365.com/elementor-page-779/)  
(Embedded securely via custom WordPress plugin)

---

## ✨ Features

- 🧠 **Conversational Prompt Engine** – Human, non-scripted coaching style using Gemini 1.5
- 🧑‍💻 **Custom Chat UI** – Avatar, typing indicator, responsive layout
- 💬 **Empathy Engine** – Dynamic tone recognition and variation
- 🌐 **WordPress Integration** – Plugin-embedded iframe, slug-based display
- ☁️ **Always-On Hosting** – Deployed on Render Pro Plan, no cold starts

---

## 📦 Tech Stack

| Layer       | Tech                      |
|-------------|---------------------------|
| AI Engine   | Google Gemini 2.5 via LangChain |
| Backend     | Python + Flask            |
| Hosting     | Render.com (Pro Tier)     |
| CMS         | WordPress + BuddyBoss     |
| UI Delivery | Custom iframe + Elementor |
| Deployment  | GitHub > Render           |

---

## 🛠️ Setup & Deployment

### 🔧 Requirements
- Python 3.10+
- `langchain-google-genai`, `flask`
- `.env` with `GEMINI_API_KEY`

### ⚙️ Local Setup

```bash
pip install -r requirements.txt
python app.py
```

### ☁️ Render Hosting
- Connect to GitHub, select `app.py`
- Add environment variable for `GEMINI_API_KEY`
- Deploy with 512MB+ memory plan

### 🌐 WordPress Integration
1. Upload `sobrio-chatbot-plugin.zip` via WordPress Plugins
2. Activate and link to `elementor-page-779`
3. Plugin injects custom chatbot section based on slug match

---

## 🗣️ Sobrio’s Voice

> “Let’s Talk – One Step at a Time.”

Sobrio speaks with calm clarity, emotional presence, and structured support.  
Unlike typical bots, Sobrio doesn’t repeat lines or over-promise solutions. Instead, it:
- Validates user emotions
- Offers realistic suggestions
- Asks thoughtful follow-up questions

Designed to simulate real-life coaching presence for people in recovery.

---

## 🔭 Roadmap (V2+)

| Feature | Status |
|---------|--------|
| 🧠 Session Memory | 🟡 Planning |
| 🎭 Mood-Aware Responses | 🟡 Planning |
| 📓 Recovery Journal Mode | 🔜 |
| 🔐 Member Paywall Logic (BuddyBoss) | 🔜 |
| 📈 Analytics & Usage Logs | 🔜 |
| 📱 Mobile App Wrapper (PWA) | 🔜 |
| 🧠 Crisis Keyword Detection | 🔜 |
| 🧑‍🤝‍🧑 Human-Sponsor Chat Tier | 🧠 Brainstorming |

---

## 🙌 Credits

Created by **Joel Freeman**  
With guidance from ChatGPT, Gemini, and the lived experience of recovery communities.

---

## 🪪 License

Proprietary – All rights reserved. Not for public redistribution without explicit permission.
