import os
import stripe
from flask import Blueprint, request, abort
from models import db, Order
from dotenv import load_dotenv

load_dotenv()

webhook = Blueprint("webhook", __name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")


@webhook.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        print("❌ Webhook error:", e)
        abort(400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        order_id = session.get("client_reference_id")
        if not order_id:
            print("❌ No client_reference_id")
            return {"status": "ignored"}, 200

        order = Order.query.get(int(order_id))
        if not order:
            print("❌ Order not found:", order_id)
            return {"status": "not_found"}, 200

        order.status = "paid"
        db.session.commit()

        print("✅ Order marked PAID:", order.id)

    return {"status": "success"}, 200
