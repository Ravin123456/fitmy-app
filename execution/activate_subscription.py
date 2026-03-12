"""
FitMY Execution Script: Subscription Activator

Activates or updates a user's subscription status in the database
after server-side payment verification.

Module: Payment
Directive: directives/payment_integration.md
"""

from datetime import datetime, timezone


def activate_subscription(
    user_id: str,
    subscription_id: str,
    plan_type: str,
    status: str = "active",
) -> dict:
    """
    Activate a user's subscription after payment verification.

    Args:
        user_id: Internal user ID.
        subscription_id: Stripe subscription ID.
        plan_type: 'monthly' or 'yearly'.
        status: Subscription status (default 'active').

    Returns:
        Dictionary with subscription record to be stored in database.
    """
    # TODO: Connect to database and persist subscription
    # This function prepares the record; the backend route handles DB write.

    from datetime import timedelta

    start_date = datetime.now(timezone.utc)
    if plan_type == "premium":
        end_date = start_date + timedelta(days=30)
    elif plan_type == "pro":
        end_date = start_date + timedelta(days=180)
    else:
        end_date = start_date  # Should not happen

    return {
        "user_id": user_id,
        "subscription_id": subscription_id,
        "subscription_tier": plan_type,
        "status": status,
        "subscription_start_date": start_date,
        "subscription_end_date": end_date,
    }


def deactivate_subscription(user_id: str, reason: str = "expired") -> dict:
    """
    Deactivate a user's subscription.

    Args:
        user_id: Internal user ID.
        reason: Reason for deactivation ('expired', 'cancelled', 'payment_failed').

    Returns:
        Dictionary with deactivation record.
    """
    return {
        "user_id": user_id,
        "status": "inactive",
        "reason": reason,
        "deactivated_at": datetime.now(timezone.utc).isoformat(),
    }
