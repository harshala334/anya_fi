# 📘 Anya.fi – User Guide & Use Cases

**Anya.fi** is an Agentic Financial Co-Pilot that lives inside Telegram. It doesn't just track money; it actively helps you change your behavior using psychology-based nudges.

This document outlines the core user journeys and how to interact with Anya to build wealth and curb impulse spending.

---

##  1. Onboarding & Goal Setting
**The Problem:** Users want to save but lack a concrete target, making it easy to lose motivation.
**The Solution:** Anya turns vague wishes into specific, trackable financial goals.

### **User Journey**
1.  **User:** Starts the bot with `/start`.
2.  **Anya:** Welcomes the user and asks, "What are you saving for? 🎯"
3.  **User:** "I want to save ₹1,50,000 for a Europe trip by December."
4.  **Anya:**
    *   Analyzes the intent (Goal: Europe Trip, Amount: ₹1.5L, Deadline: Dec).
    *   Calculates the monthly savings required.
    *   **Action:** Creates a goal in the database.
    *   **Response:** "Awesome! To hit ₹1.5L by December, you need to save **₹15,000/month**. I've set this up for you. Shall we track your daily spending to keep you on course?"

---

##  2. Smart Expense Tracking & Budgeting
**The Problem:** Manual tracking is tedious. Users forget to log expenses.
**The Solution:** Natural language logging and proactive budget alerts.

### **User Journey**
1.  **User:** "Spent ₹450 on coffee and snacks at Starbucks."
2.  **Anya:**
    *   **Categorization:** Automatically tags as `Dining/Food`.
    *   **Budget Check:** Checks if this pushes the user over their monthly limit.
    *   **Response:** "Got it. ☕ That brings your Dining spend to ₹4,500 this month. You have ₹500 left in your weekly 'Fun Budget'. Tread carefully!"

### **Commands**
*   `/mystats` – Shows a text summary of your budget status (Green/Orange/Red).
*   `/dashboard` – Generates a link to your **Visual Dashboard** with progress bars and charts.

---

##  3. The "Anti-Impulse" Intervention
**The Problem:** Late-night doom scrolling on shopping sites leads to regretful purchases.
**The Solution:** Real-time intervention before the checkout happens.

### **User Journey**
1.  **Context:** User is browsing Amazon/Flipkart and adds a ₹30,000 gadget to the cart.
2.  **System:** The **Anya Chrome Extension** detects the high-value cart item.
3.  **Anya (on Telegram):** *Immediately sends a notification.*
    *   "🚨 **Impulse Alert!** I see you're eyeing that ₹30,000 gadget."
    *   "Remember your **Europe Trip** goal? That ₹30k is **2 months of savings**."
    *   "Do you really need this now, or can it wait 30 days?"
4.  **Result:** The user pauses, re-evaluates, and often abandons the cart to protect their long-term goal.

---

##  4. Future-Self Synthesizer
**The Problem:** "Saving" feels like a sacrifice today for a vague tomorrow.
**The Solution:** Make the future feel real and emotional.

### **User Journey**
1.  **User:** Feels tempted to break their savings streak.
2.  **User:** `/dream Paris Vacation`
3.  **Anya:**
    *   Uses AI to generate a hyper-realistic image of the user (or a POV shot) in Paris.
    *   **Response:** *[Sends Image of a cafe in Paris]*
    *   "This is what you're working towards, [Name]. Don't trade this view for a temporary purchase today. Keep going! "

---

##  5. Social Currency Optimizer
**The Problem:** Peer pressure ("Let's go to that expensive club!") destroys budgets.
**The Solution:** Anya suggests cool but cheaper alternatives to save face and money.

### **User Journey**
1.  **User:** "Friends want to go for drinks in Indiranagar, but I'm broke. Help!"
2.  **User:** `/social Drinks Indiranagar`
3.  **Anya:**
    *   Scans for budget-friendly but "vibe-checked" places.
    *   **Response:** "Skip the overpriced clubs! Try **Toit** or **Bob's Bar**. Great ambience, craft beers, and you'll spend 50% less. Plus, it's a cooler spot for a chill evening. 🍻"

---

##  6. Visual Dashboard
**The Problem:** Chat logs are hard to read for big-picture analysis.
**The Solution:** A dedicated web view for financial health.

### **User Journey**
1.  **User:** `/dashboard`
2.  **Anya:** "Here is your personal financial cockpit: [Link]"
3.  **User:** Clicks the link to see:
    *   **Goal Progress:** A progress bar filling up towards the Europe Trip.
    *   **Budget Dial:** A gauge showing 70% of the monthly budget used.
    *   **Recent Transactions:** A clean list of where money went this week.

---


**Anya.fi** is not just a chatbot; it's a **behavioral modification engine**. By combining:
1.  **Frictionless Tracking** (NLP)
2.  **Real-time Interventions** (Chrome Extension)
3.  **Emotional Anchoring** (Generative AI)
4.  **Social Intelligence** (Alternative recommendations)

...we bridge the gap between *knowing* you should save and *actually* doing it.
