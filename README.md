# E-Commerce Shopping Chatbot Using Python and Flask

## 1. Introduction
ShopEase AI is a modern, customer-facing e-commerce web application featuring a product catalog, secure payment integration, and an AI-powered shopping chatbot to assist users.

## 2. Problem Statement
Many e-commerce websites lack real-time personalized assistance. This project solves that by integrating a conversational AI assistant directly into the shopping experience.

## 3. Objectives
- Build a complete e-commerce flow from product browsing to order confirmation.
- Implement an AI-driven chatbot for product recommendations.
- Integrate a secure mock payment gateway for testing and viva purposes.

## 4. Features
- Fully responsive modern UI
- Product search & filtering
- Shopping cart functionality
- AI Chatbot using Google Gemini API
- Secure Test Payment Gateway (Cards, UPI, NetBanking, COD)
- Order Tracking System

## 5. Technologies Used
- **Backend:** Python 3, Flask
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **AI Integration:** Google Generative AI API

## 6. System Requirements
- Python 3.8+
- Modern Web Browser
- Internet Connection (for AI and images)

## 7. Project Structure
`app.py`: Main Flask application.
`database/`: SQLite database and seed scripts.
`templates/`: HTML templates.
`static/`: CSS, JS, and Images.

## 8. Installation

1. **Clone or Extract the Project**
2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   ```
3. **Activate the Virtual Environment (Windows):**
   ```bash
   venv\Scripts\activate
   ```
4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Setup Environment Variables:**
   Rename `.env.example` to `.env` and add your Google API key for the chatbot.

6. **Initialize Database:**
   ```bash
   python database/seed.py
   ```

7. **Run the Application:**
   ```bash
   python app.py
   ```
   Open `http://127.0.0.1:5000` in your browser.

## 9. How to Demonstrate
1. **Browse Products:** Show the homepage and catalog.
2. **Chatbot:** Open the bot, ask about "laptops under 50000".
3. **Cart & Checkout:** Add a product, fill checkout details.
4. **Payment:** Use the Sandbox payment page to complete a transaction.
5. **Tracking:** Use the generated Order ID to track the status.
