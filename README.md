# Flask E-Commerce Application with Stripe Payments

A full-stack e-commerce web application built with **Flask** that demonstrates real-world backend and full-stack engineering concepts such as authentication, admin roles, payment processing, Stripe webhooks, and order lifecycle management.

This project is intentionally built as a **portfolio showcase** to demonstrate practical software engineering skills rather than as a production SaaS.

---

## 🚀 Features

### User Features
- User registration and login
- Browse products
- Secure checkout with Stripe
- Automatic order confirmation after payment
- Order status tracking

### Admin Features
- Admin dashboard
- Add, edit, and delete products
- Upload and manage product images
- View all orders
- Mark paid orders as **Shipped**

### Payment System
- Stripe Checkout integration
- Stripe Webhooks for server-side payment verification
- Secure order status updates
- Prevents manual or fake payment confirmation

---

## 🧠 Architecture Overview

- **Flask** for routing and application logic
- **SQLAlchemy** as ORM
- **Flask-Login** for authentication
- **Stripe API** for payments
- **Stripe Webhooks** for payment confirmation
- **SQLite** for local / portfolio use
- **PostgreSQL-ready** via environment variables

---

## 🛠 Tech Stack

- **Backend:** Python (Flask)
- **Database:** SQLite (default), PostgreSQL (optional)
- **ORM:** SQLAlchemy
- **Authentication:** Flask-Login
- **Payments:** Stripe Checkout + Webhooks
- **Frontend:** Jinja2, Bootstrap
- **Deployment:** Render-compatible

---

## 📁 Project Structure

ECOMMERCE/
├── pycache/
├── instance/
│ └── ecommerce.db
├── migrations/
├── static/
│ ├── css/
│ │ └── store.css
│ ├── images/
│ │ ├── ck-jeans.jpg
│ │ ├── tommi-jeans.jpg
│ │ ├── tommi-longtj.jpg
│ │ └── tommi-tshirt.jpg
│ └── uploads/
├── templates/
│ ├── admin/
│ │ ├── dashboard.html
│ │ ├── edit_product.html
│ │ ├── orders.html
│ │ └── products.html
│ ├── base.html
│ ├── cart.html
│ ├── login.html
│ ├── orders.html
│ ├── product.html
│ ├── register.html
│ ├── store.html
│ └── success.html
├── .env
├── .gitignore
├── api.py
├── app.py
├── config.py
├── models.py
├── webhook.py
├── requirements.txt
└── README.md

---

## ⚙️ Running Locally

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/WiraAFauzi/flask-ecommerce-stripe.git
cd flask-ecommerce-stripe

### 2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate
# Windows: venv\Scripts\activate

### 3️⃣ Install Dependencies
pip install -r requirements.txt

### 4️⃣ Environment Variables

Create a .env file in the project root:

SECRET_KEY=your_secret_key
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

### 5️⃣ Run the App
python app.py

# Application runs at:
http://localhost:5000

### 💳 Stripe Webhook (Local Testing)

# Install Stripe CLI:
https://stripe.com/docs/stripe-cli

# Login:
stripe login

# Forward webhooks:
stripe listen --forward-to localhost:5000/webhook

# Stripe test card:
4242 4242 4242 4242
Any future expiry
Any CVC

### 👑 Creating an Admin User

# Admin access is controlled by an is_admin flag.

# Using Flask Shell
flask shell

from models import db, User

user = User.query.filter_by(email="admin@example.com").first()
user.is_admin = True
db.session.commit()

# Log out and log back in to access the admin dashboard.

👤 Author

Wira bin Ahmad Fauzi
Aspiring Software Engineer
Backend & Full-Stack Development