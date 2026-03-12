# Directive: Payment Integration

## Objective
Integrate Stripe with FPX support for Malaysian users to handle subscription payments. All payment verification must happen server-side via webhook — never trust the frontend.

## Inputs
- **Checkout:** user ID, plan type (monthly / yearly)
- **Webhook:** Stripe event payload + signature
- **Status check:** user ID or subscription ID

## Outputs
- Stripe Checkout Session URL (redirect user to Stripe)
- Subscription activation in database
- Subscription status (active / expired / cancelled)
- Payment receipts

## Required Tools / Scripts
- `execution/create_checkout_session.py` — Create Stripe Checkout session with FPX
- `execution/verify_webhook.py` — Validate webhook signature and process event
- `execution/activate_subscription.py` — Update database subscription status
- `execution/subscription_status.py` — Check current subscription validity

## Payment Flow
1. User selects plan → backend creates Checkout Session → redirect to Stripe
2. User pays via FPX / card → Stripe sends webhook to backend
3. Backend verifies webhook signature
4. Backend activates subscription in database
5. Frontend checks subscription status on next load

## Edge Cases
- Webhook arrives before redirect callback — subscription should still activate
- Duplicate webhook events — idempotent processing (check if already processed)
- Payment fails — do not activate subscription, log failure
- Subscription expires — block premium features, show upgrade prompt
- Stripe API downtime — queue retry, show user a pending state
- User cancels mid-checkout — no action needed (webhook won't fire)

## Validation Rules
- [ ] Webhook signature is always verified before processing
- [ ] Subscription never activated from frontend-only data
- [ ] Webhook processing is idempotent
- [ ] Expired subscriptions correctly block premium features
- [ ] All Stripe API keys are in `.env`, never in code
- [ ] FPX is enabled as a payment method in Checkout session
