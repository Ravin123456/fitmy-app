"""
FitMY Execution Script: Stripe Checkout Session Creator

Creates a Stripe Checkout Session with FPX support for Malaysian payments.

Module: Payment
Directive: directives/payment_integration.md
"""

import os

import stripe
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")


def create_checkout_session(
    user_id: str,
    plan_type: str,
    success_url: str,
    cancel_url: str,
) -> dict:
    """
    Create a Stripe Checkout Session.

    Args:
        user_id: The internal user ID (stored in metadata).
        plan_type: 'monthly' or 'yearly'.
        success_url: URL to redirect after successful payment.
        cancel_url: URL to redirect if user cancels.

    Returns:
        Dictionary with 'session_id' and 'checkout_url'.

    Raises:
        ValueError: If plan_type is not 'monthly' or 'yearly'.
        stripe.error.StripeError: If Stripe API call fails.
    """
    price_ids = {
        "premium": os.getenv("STRIPE_PRICE_ID_PREMIUM", "price_premium_placeholder"),
        "pro": os.getenv("STRIPE_PRICE_ID_PRO", "price_pro_placeholder"),
    }

    plan_type = plan_type.strip().lower()
    if plan_type not in price_ids:
        raise ValueError(f"Invalid plan_type '{plan_type}'. Must be 'premium' or 'pro'.")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_ids[plan_type],
                "quantity": 1,
            }
        ],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"user_id": user_id, "plan_type": plan_type},
    )

    return {
        "session_id": session.id,
        "checkout_url": session.url,
    }
