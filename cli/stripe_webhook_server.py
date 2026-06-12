import os
import stripe
from flask import Flask, request, jsonify
from drift_entitlement import handle_purchase, TIER_ACCESS

# Initialize Flask App
app = Flask(__name__)

# --- CONFIGURATION ---
# Using the test API keys provided for PHI//DRIFT
stripe.api_key = os.environ.get("STRIPE_API_KEY", "sk_test_YOUR_STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_YOUR_STRIPE_WEBHOOK_SECRET")

# Domain configuration
DOMAIN = "https://phidrift.com"

# A mapping from Stripe Price IDs to DRIFT Product/Tier IDs
# Run `setup_stripe_products.py` to generate the real Price IDs and paste them here.
STRIPE_PRICE_MAP = {
    "price_1ThMjNJ300BL6srDYZMOsXwj": "drift_whitepaper",
    "price_1ThMjOJ300BL6srDtFml0KX7": "cognitive_loop_guide",
    "price_1ThMjOJ300BL6srDUv18glAl": "forge_starter_kit",
    "price_1ThMjOJ300BL6srDieqx1huv": "lotus_cyber_module",
    "price_1ThMjPJ300BL6srDb77QGfoS": "mouse_bug_bot",
    "price_1ThMjPJ300BL6srDQwq9IoAz": "forge_operator",
    "price_1ThMjPJ300BL6srDYi0xvTkn": "inner_circle",
}

@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", "")

    try:
        # Verify the webhook signature to ensure it actually came from Stripe
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        print("⚠️ [WEBHOOK ERROR] Invalid payload.")
        return jsonify({"error": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print("⚠️ [WEBHOOK ERROR] Invalid Stripe signature.")
        return jsonify({"error": "Invalid signature"}), 400

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        
        # Get customer email
        email = session.get("customer_details", {}).get("email")
        if not email:
            print("⚠️ [WEBHOOK ERROR] No email found in checkout session.")
            return jsonify({"error": "Missing email"}), 400

        try:
            line_items = stripe.checkout.Session.list_line_items(session["id"])
            for item in line_items["data"]:
                price_id = item["price"]["id"]
                drift_item = STRIPE_PRICE_MAP.get(price_id)
                
                if drift_item:
                    print(f"✅ [STRIPE] Valid tip/purchase detected: {email} unlocked {drift_item}")
                    # Trigger the DRIFT Entitlement Engine!
                    handle_purchase(email, drift_item)
                else:
                    print(f"⚠️ [STRIPE] Unknown Price ID ({price_id}) purchased by {email}. No DRIFT action taken.")
        except Exception as e:
            print(f"⚠️ [WEBHOOK ERROR] Failed to process line items: {e}")
            return jsonify({"error": "Failed to process items"}), 500

    return jsonify({"status": "success"}), 200

# Endpoint to generate a checkout session link (which you can link on your site)
@app.route("/checkout/<drift_id>", methods=["GET"])
def create_checkout_session(drift_id):
    # Reverse lookup to find the Stripe Price ID for a given DRIFT product ID
    price_id = None
    for p_id, d_id in STRIPE_PRICE_MAP.items():
        if d_id == drift_id:
            price_id = p_id
            break
            
    if not price_id:
        return jsonify({"error": "Invalid product ID"}), 404
        
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{DOMAIN}/cancel",
        )
        # Redirect the user to the Stripe Checkout page
        return jsonify({"checkout_url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print(f"🔥 Starting DRIFT Webhook Server mapped to {DOMAIN}...")
    print("Waiting for Stripe events...")
    # Run the server on port 4242
    app.run(host="0.0.0.0", port=4242)
