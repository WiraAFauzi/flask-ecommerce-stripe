from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


# ---------------- USER ----------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # Admin flag
    is_admin = db.Column(db.Boolean, default=False)


# ---------------- PRODUCT ----------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)

    price = db.Column(db.Float, nullable=False)

    image = db.Column(db.String(120), default="default.jpg")


# ---------------- ORDER ----------------
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Who bought it
    user_email = db.Column(db.String(120), nullable=False)

    # Snapshot of product at purchase time
    product_name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)

    # Stripe
    stripe_session_id = db.Column(db.String(255), unique=True, nullable=True)

    # pending → paid → cancelled
    status = db.Column(db.String(20), default="pending")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
