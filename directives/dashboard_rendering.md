# Directive: Dashboard Rendering

## Objective
Display a personalised dashboard showing the user's daily overview: calorie intake, today's workout, weight progress, budget tracking, and streak data.

## Inputs
- User ID (from authenticated session)

## Outputs
- Today's calorie summary (target vs consumed)
- Today's workout plan
- Weight history chart data
- Budget tracking (daily spent vs budget)
- Current streak count

## Required Tools / Scripts
- `execution/fetch_user_data.py` — Aggregate user's daily data
- `execution/weight_log_handler.py` — CRUD operations for weight entries
- `execution/generate_progress_chart.py` — Format data for chart rendering
- `execution/streak_counter.py` — Calculate consecutive active days

## Edge Cases
- New user with no data — show onboarding prompt instead of empty dashboard
- No weight entries — hide weight chart, show prompt to log first entry
- Streak broken — show motivational reset message
- Data from different timezones — normalise to user's timezone (Malaysia: UTC+8)

## Validation Rules
- [ ] Dashboard only shows data belonging to the authenticated user
- [ ] Weight chart handles missing days gracefully (interpolation or gaps)
- [ ] Streak count is accurate to UTC+8 day boundaries
- [ ] All monetary values displayed in RM
- [ ] Dashboard loads within 2 seconds
