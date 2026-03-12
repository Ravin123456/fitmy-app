"""
FitMY Execution Script: Subscription Status Checker

Checks whether a user has an active, valid subscription.

Module: Payment
Directive: directives/payment_integration.md
"""

from datetime import datetime, timezone


def check_subscription_status(subscription_record: dict | None) -> dict:
    """
    Check if a subscription is currently active and valid.

    Args:
        subscription_record: The stored subscription dictionary,
                             or None if no subscription exists.

    Returns:
        Dictionary with:
            - is_active: bool
            - plan_type: str or None
            - status: str
            - message: str
    """
    if subscription_record is None:
        return {
            "is_active": False,
            "plan_type": None,
            "status": "none",
            "message": "No subscription found. Upgrade to premium for full access.",
        }

    status = subscription_record.get("status", "inactive")

    if status == "active":
        return {
            "is_active": True,
            "plan_type": subscription_record.get("plan_type"),
            "status": "active",
            "message": "Your premium subscription is active.",
        }
    elif status == "cancelled":
        return {
            "is_active": False,
            "plan_type": subscription_record.get("plan_type"),
            "status": "cancelled",
            "message": "Your subscription has been cancelled.",
        }
    else:
        return {
            "is_active": False,
            "plan_type": subscription_record.get("plan_type"),
            "status": status,
            "message": "Your subscription is inactive. Please renew to access premium features.",
        }


def is_premium_user(subscription_record: dict | None) -> bool:
    """
    Quick check: does this user have active premium access?

    Args:
        subscription_record: The stored subscription dictionary or None.

    Returns:
        True if user has an active subscription.
    """
    return check_subscription_status(subscription_record)["is_active"]
