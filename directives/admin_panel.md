# Directive: Admin Panel

## Objective
Provide an admin interface to manage users, view subscriptions, monitor system health, and manage the Malaysian food database.

## Inputs
- Admin credentials (email + password with admin role)

## Outputs
- User management: list, search, view, suspend, delete users
- Subscription overview: active, expired, cancelled counts
- Food database management: add, edit, delete food items
- System health metrics: API response times, error rates

## Required Tools / Scripts
- `execution/fetch_user_data.py` (reused — admin mode)
- `execution/subscription_status.py` (reused — bulk query)
- `execution/input_sanitization.py` — Sanitise all admin inputs
- `execution/error_logger.py` — View error logs

## Edge Cases
- Non-admin user tries to access admin routes — 403 Forbidden
- Admin deletes own account — prevent with validation
- Bulk operations timeout — paginate and process in batches
- Food item deletion while referenced in active meal plans — soft-delete only

## Validation Rules
- [ ] Admin routes require JWT with `role: admin`
- [ ] All admin actions are logged with timestamp and admin user ID
- [ ] Food database changes take effect on next meal plan generation (not retroactively)
- [ ] User deletion is soft-delete (data retained for 30 days)
- [ ] Admin panel is not accessible from public URLs without authentication
