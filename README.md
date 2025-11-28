# Anya.fi – Agentic Financial Co-Pilot on WhatsApp & Telegram

Stop managing money. Start building wealth.

---

## 📌 Overview

Most financial apps fail because they expect discipline from users who are already overwhelmed. Dashboards and budgets don’t change behavior — timely, contextual, psychologically aware guidance does.

**Anya.fi** is a proactive Agentic AI that lives inside **WhatsApp and Telegram**, not a standalone mobile app.  
It analyzes financial activity in real time and nudges users using human-like, empathetic conversation.

---

## ❗ Problem We Solve

Traditional financial apps are:

- Passive dashboards  
- Information-heavy  
- Not behavior-changing  
- Built for users with time & discipline  

For gig workers, freelancers & stressed millennials:

- Income is volatile  
- Spending is unpredictable  
- No one has time for budgeting  

They need **guidance, not graphs**.

---

## 🌟 Our Solution: Chat-First Financial Co-Pilot

### Core Principles
- **Zero Input** — No manual logging or categorization  
- **Proactive AI Assistant**  
- **Conversational nudges instead of notifications**  
- **Lives on WhatsApp & Telegram**  
- **Uses Account Aggregator for secure data**  
- **Behavioral psychology-driven design**  

---

## 🧠 Core Experience

### ✔ User chats with Anya on WhatsApp or Telegram  
### ✔ Anya ingests transactions using Account Aggregator  
### ✔ LLM interprets spending context  
### ✔ Agent orchestrates plugins automatically  
### ✔ Chat messages deliver personalized nudges  

---

## 🏗 Architecture

```
                [User] 
                   |
         WhatsApp / Telegram Bots
                   |
          ┌────────────────────┐
          │ Messaging Adapters │
          └────────────────────┘
                   |
          ┌────────────────┐
          │     MCP Layer  │
          │  (Agent Brain) │
          └────────────────┘
        Observe → Reason → Act
                   |
          ┌──────────────────┐
          │     LLM Core     │
          └──────────────────┘
       /       |         |         \
Account   GoalTracker   Plugins     Tools
Aggregator    DB      (Zomato,   (Browser ext,
   API                 MagicBricks, AA Consent)
                     PaytmInsider)
```

---

## 🔌 Plugin Ecosystem

### **1️⃣ Anti-Impulse Sphere**
Detects checkout pages via browser extension → triggers intervention via WhatsApp/Telegram.

### **2️⃣ Future-Self Synthesizer**
Generates personalized images of the user’s dream home or long-term goals using real real-estate data.

### **3️⃣ Social Currency Optimizer**
Recommends socially intelligent alternatives when peer pressure causes costly plans.

---

## 🛠 Tech Stack (Fixed Best Choices)

### **Backend**
- **FastAPI (Python)**  
- **PostgreSQL (Primary Database)**  
- **Redis (Agent memory + session state)**  
- **SQLAlchemy ORM**

### **AI Layer**
- **OpenAI LLM (Agent Brain)**  
- **Model Context Protocol (MCP) for tool orchestration**  
- **Image Generation: OpenAI / Gemini**

### **Integrations**
- **Account Aggregator (Finvu Sandbox)**  
- **Zomato API**  
- **MagicBricks / 99acres APIs**  
- **PaytmInsider API**

### **User-Facing Messaging**
- **WhatsApp Business Cloud API**  
- **Telegram Bot API**  
- **Chrome Extension (Anti-Impulse Plugin)**  

### **Deployment**
- **Docker**  
- **Railway / Render for backend**  
- **Ngrok for local webhook testing**

---

## 🚀 Development Roadmap

---

### **Phase 0 — Pre-Build Setup**

- Create WhatsApp Business App  
- Create Telegram Bot using BotFather  
- Configure webhook + verify tokens  
- Setup FastAPI project structure  
- Initialize PostgreSQL + schemas  
- Register with A.A sandbox  
- Setup Redis for session state  
- Create `.env` and config management  

---

### **Phase 1 — MVP**

#### 🎯 Features
- WhatsApp + Telegram bot both live  
- AA consent + fetch transactions  
- Transaction categorization  
- Goals storage  
- MCP loop: Observe → Reason → Act  
- Basic nudges delivered via WhatsApp  

#### 🎯 User Flow
1. User: “I want to save for a laptop”  
2. System stores goal  
3. When overspending occurs → friendly nudge on WhatsApp & Telegram  

---

### **Phase 2 — Plugin Development**

#### 🟣 Plugin 1: Anti-Impulse Sphere
- Build Chrome extension  
- Detect checkout URLs  
- Emit event → backend  
- Trigger AI intervention  

#### 🟡 Plugin 2: Future-Self Synthesizer
- Fetch real estate data  
- Generate emotional future-goal image  
- Assign as goal thumbnail  

#### 🟢 Plugin 3: Social Currency Optimizer
- Fetch location + alternatives  
- Draft socially intelligent message  
- Deliver via WhatsApp & Telegram  

---

### **Phase 3 — Full Product Hardening**

- Reliability improvements  
- Better conversation memory  
- User analytics dashboard  
- Auto-savings workflows  
- Personalized investment nudges  
- Behavioral insights engine  

---

## 🧩 Folder Structure

```
anya-fi/
 ├── backend/
 │    ├── main.py
 │    ├── agents/
 │    │     ├── mcp.py
 │    │     ├── impulse_agent.py
 │    │     ├── future_self_agent.py
 │    │     ├── social_agent.py
 │    ├── messaging/
 │    │     ├── whatsapp.py
 │    │     ├── telegram.py
 │    ├── plugins/
 │    ├── whatsapp/
 │    ├── db/
 │    │     ├── models.py
 │    │     ├── migrations/
 │    ├── utils/
 │    └── config.py
 ├── chrome-extension/
 ├── docs/
 │    └── architecture.png
 └── README.md
```

---

## 🧪 How to Run Locally

```
git clone https://github.com/asyelmoteb22-show/anya-shop-guardian.git
cd anya-shop-guardian

# setup env
cp .env.example .env

# install backend deps
pip install -r requirements.txt

# run FastAPI
uvicorn main:app --reload
```

---

## 🌱 Future Roadmap

- Multilingual support  
- Instagram support  
- Automated SIP + investment plans  
- Emotional-AI personality modes  
- Tax advisory assistant  
- Personalized bill negotiation AI  

---

## 📄 License
MIT License  
© 2025 Anya.fi Team
