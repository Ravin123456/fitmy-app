"""
FitMY Execution Script: Stripe Webhook Verifier

Validates Stripe webhook signatures and extracts event data.
CRITICAL: Never process a webhook without verifying the signature first.

Module: Payment
Directive: directives/payment_integration.md
"""

import os

import stripe
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")


def verify_webhook(payload: bytes, signature: str) -> dict:
    """
    Verify a Stripe webhook signature and return the event.

    Args:
        payload: Raw request body bytes.
        signature: Value of the 'Stripe-Signature' header.

    Returns:
        The verified Stripe event as a dictionary.

    Raises:
        stripe.error.SignatureVerificationError: If signature is invalid.
        ValueError: If webhook secret is not configured.
    """
    if not WEBHOOK_SECRET:
        raise ValueError("STRIPE_WEBHOOK_SECRET is not configured in .env")

    event = stripe.Webhook.construct_event(
        payload, signature, WEBHOOK_SECRET
    )
    return event


def extract_subscription_data(event: dict) -> dict | None:
    """
    Extract subscription-relevant data from a webhook event.

    Args:
        event: Verified Stripe event dictionary.

    Returns:
        Dictionary with user_id, subscription_id, status, plan_type.
        None if event type is not subscription-related.
    """
    relevant_events = [
        "checkout.session.completed",
        "customer.subscription.updated",
        "customer.subscription.deleted",
        "invoice.payment_succeeded",
        "invoice.payment_failed",
    ]

    event_type = event.get("type", "")
    if event_type not in relevant_events:
        return None

    data = event.get("data", {}).get("object", {})
    metadata = data.get("metadata", {})

    return {
        "event_type": event_type,
        "user_id": metadata.get("user_id"),
        "subscription_id": data.get("subscription") or data.get("id"),
        "status": data.get("status"),
        "plan_type": metadata.get("plan_type"),
    }
