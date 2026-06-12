import os
import stripe

# Use the key from environment variables
stripe.api_key = os.environ.get("STRIPE_API_KEY", "sk_test_YOUR_STRIPE_SECRET_KEY")

PRODUCTS_TO_CREATE = [
    {
        "id": "drift_whitepaper",
        "name": "DRIFT Whitepaper",
        "description": "Full DRIFT architecture breakdown and blueprints.",
        "price_usd": 15
    },
    {
        "id": "cognitive_loop_guide",
        "name": "Build Your Own Cognitive Loop",
        "description": "Step-by-step masterclass on designing adaptive AI loops.",
        "price_usd": 25
    },
    {
        "id": "forge_starter_kit",
        "name": "Forge Testing Framework PRO",
        "description": "The production-ready harness for deep causal perturbation.",
        "price_usd": 35
    },
    {
        "id": "lotus_cyber_module",
        "name": "LOTUS Academy: Beginner Cybersecurity",
        "description": "Foundational cybersecurity training with hands-on lessons.",
        "price_usd": 20
    },
    {
        "id": "forge_operator",
        "name": "Forge Operator Tier",
        "description": "Unlock advanced tools, guides, and the whitepaper.",
        "price_usd": 75
    },
    {
        "id": "inner_circle",
        "name": "Inner Circle Tier",
        "description": "All access pass plus priority beta features.",
        "price_usd": 150
    }
]

def setup_stripe_products():
    print("🔥 Starting Stripe Configuration...")
    price_map = {}
    
    for prod in PRODUCTS_TO_CREATE:
        try:
            print(f"Creating Product: {prod['name']}...")
            # Create the Product
            stripe_product = stripe.Product.create(
                name=prod['name'],
                description=prod['description'],
                metadata={"drift_id": prod["id"]}
            )
            
            # Create the Price
            stripe_price = stripe.Price.create(
                product=stripe_product.id,
                unit_amount=prod['price_usd'] * 100, # Amount in cents
                currency="usd",
            )
            
            price_map[stripe_price.id] = prod["id"]
            print(f"  ✅ Created! Price ID: {stripe_price.id}")
            
        except stripe.error.AuthenticationError:
            print("\n❌ [ERROR] Authentication Failed. Your Stripe API Key is truncated or invalid.")
            print("Please double check your secret key. It should look like 'sk_live_...' or 'sk_test_...' and be much longer.")
            return
        except Exception as e:
            print(f"  ❌ Error: {e}")

    print("\n✅ Setup Complete! Update your stripe_webhook_server.py with this map:")
    print("STRIPE_PRICE_MAP = {")
    for price_id, drift_id in price_map.items():
        print(f'    "{price_id}": "{drift_id}",')
    print("}")
    
    print("\nRemember to configure your webhook endpoint in the Stripe Dashboard to point to:")
    print("https://phidrift.com/webhook")

if __name__ == "__main__":
    setup_stripe_products()
