#!/usr/bin/env python3
"""
DRIFT Entitlement & Monetization Engine
The feedback-driven intelligence system for managing user access and tiers.
"""
import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Enforce durable state location per rule
DRIFT_OS_DATA = Path("/home/crexs/.drift_os/monetization")
DRIFT_OS_DATA.mkdir(parents=True, exist_ok=True)

# 1. Tier -> Access Mapping (The Brain)
TIER_ACCESS = {
    "signal_booster": {
        "posts": True,
        "dev_logs": False,
        "downloads": []
    },
    "system_architect": {
        "posts": True,
        "dev_logs": True,
        "downloads": ["drift_whitepaper"]
    },
    "forge_operator": {
        "posts": True,
        "dev_logs": True,
        "downloads": [
            "drift_whitepaper",
            "cognitive_loop_guide",
            "forge_starter_kit"
        ]
    },
    "inner_circle": {
        "posts": True,
        "dev_logs": True,
        "downloads": "ALL",
        "priority_access": True
    }
}

# 2. User State Model
class User:
    def __init__(self, email):
        self.email = email
        self.tier = None
        self.products = []
        self.state = {
            "access_level": 0,
            "permissions": {},
            "history": []
        }

    def to_dict(self):
        return {
            "email": self.email,
            "tier": self.tier,
            "products": self.products,
            "state": self.state
        }

    @classmethod
    def from_dict(cls, data):
        u = cls(data["email"])
        u.tier = data.get("tier")
        u.products = data.get("products", [])
        u.state = data.get("state", {"access_level": 0, "permissions": {}, "history": []})
        return u

class UserDB:
    def _get_path(self, email):
        safe_email = email.replace("@", "_at_").replace(".", "_dot_")
        return DRIFT_OS_DATA / f"user_{safe_email}.json"

    def get_user(self, email):
        path = self._get_path(email)
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return User.from_dict(json.load(f))
        return None

    def create_user(self, email):
        if self.get_user(email):
            print(f"[SYSTEM] User {email} already exists.")
            return self.get_user(email)
        u = User(email)
        self.save(u)
        print(f"[SYSTEM] Created user: {email}")
        return u

    def save(self, user):
        path = self._get_path(user.email)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(user.to_dict(), f, indent=2)

db = UserDB()

# 4. Dynamic Unlock Engine
def unlock(user):
    permissions = user.state.get("permissions", {})
    print(f"\n🔓 [DRIFT DYNAMIC UNLOCK ENGINE] Processing entitlements for {user.email}")
    
    downloads = permissions.get("downloads", [])
    if downloads == "ALL":
        print("  ▸ GRANTING ALL DOWNLOADS (Inner Circle Access)")
    else:
        for item in downloads:
            print(f"  ▸ GRANTING DOWNLOAD: {item}")
            
    # Also unlock individual standalone products
    for product in user.products:
        print(f"  ▸ GRANTING DOWNLOAD (A La Carte): {product}")

    if permissions.get("dev_logs"):
        print("  ▸ GRANTING ACCESS: dev_logs")

    if permissions.get("priority_access"):
        print("  ▸ GRANTING ACCESS: beta_features")
        
    print("  [SUCCESS] All entitlements synced dynamically.")

# 3. Purchase Event -> DRIFT Hook
def handle_purchase(email, product_or_tier):
    user = db.get_user(email) or db.create_user(email)

    if product_or_tier in TIER_ACCESS:
        user.tier = product_or_tier
        user.state["permissions"] = TIER_ACCESS[product_or_tier]
        print(f"[DRIFT] Upgraded {email} to tier: {product_or_tier}")
    else:
        if product_or_tier not in user.products:
            user.products.append(product_or_tier)
            print(f"[DRIFT] Added product '{product_or_tier}' to {email}")

    user.state["history"].append({
        "event": "purchase",
        "item": product_or_tier,
        "timestamp": datetime.now().isoformat()
    })
    
    # 7. Adaptive AI Hooks (The Future)
    # Give the system some basic rules to calculate state evolution
    user.state["access_level"] = len(user.products) + (10 if user.tier else 0)

    db.save(user)
    unlock(user)

# 5. CLI Commands
def main():
    parser = argparse.ArgumentParser(description="DRIFT Entitlement Engine CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # user:create
    p_create = subparsers.add_parser("user:create", help="Create a user manually")
    p_create.add_argument("--email", required=True)

    # user:set-tier
    p_set_tier = subparsers.add_parser("user:set-tier", help="Grant a tier to a user")
    p_set_tier.add_argument("--email", required=True)
    p_set_tier.add_argument("--tier", required=True, choices=TIER_ACCESS.keys())

    # user:grant
    p_grant = subparsers.add_parser("user:grant", help="Grant a single product to a user")
    p_grant.add_argument("--email", required=True)
    p_grant.add_argument("--product", required=True)

    # user:inspect
    p_inspect = subparsers.add_parser("user:inspect", help="View a user's permissions and history")
    p_inspect.add_argument("--email", required=True)
    
    # webhook:simulate
    p_webhook = subparsers.add_parser("webhook:simulate", help="Simulate a Stripe Webhook purchase event")
    p_webhook.add_argument("--email", required=True)
    p_webhook.add_argument("--item", required=True, help="Product ID or Tier Name")

    args = parser.parse_args()

    if args.command == "user:create":
        db.create_user(args.email)
        
    elif args.command == "user:set-tier":
        user = db.get_user(args.email) or db.create_user(args.email)
        handle_purchase(args.email, args.tier)
        
    elif args.command == "user:grant":
        user = db.get_user(args.email) or db.create_user(args.email)
        handle_purchase(args.email, args.product)
        
    elif args.command == "user:inspect":
        user = db.get_user(args.email)
        if not user:
            print(f"[ERROR] User {args.email} not found.")
            return
        print(f"\n=== INSPECTING: {user.email} ===")
        print(f"Tier: {user.tier}")
        print(f"Products: {user.products}")
        print(f"State: {json.dumps(user.state, indent=2)}")
        print("===============================\n")
        
    elif args.command == "webhook:simulate":
        print(f"[STRIPE WEBHOOK] Simulating checkout.session.completed for {args.email} -> {args.item}")
        handle_purchase(args.email, args.item)

if __name__ == "__main__":
    main()
