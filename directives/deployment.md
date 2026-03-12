# Directive: Deployment

## Objective
Deploy the FitMY application to production using Vercel (frontend) and Railway (backend + database).

## Inputs
- Production-ready codebase (all tests passing)
- Environment variables for production
- Domain name (optional)

## Outputs
- Frontend deployed to Vercel with custom domain
- Backend deployed to Railway with PostgreSQL
- Environment variables configured in both platforms
- SSL/TLS active on all endpoints

## Required Tools / Scripts
- Vercel CLI or GitHub integration
- Railway CLI or GitHub integration
- Database migration scripts (`alembic`)

## Deployment Steps

### Backend (Railway)
1. Connect GitHub repository to Railway
2. Set Python buildpack
3. Configure environment variables in Railway dashboard
4. Provision PostgreSQL add-on
5. Run database migrations: `alembic upgrade head`
6. Set start command: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)
1. Connect GitHub repository to Vercel
2. Set root directory to `/frontend`
3. Configure API base URL environment variable
4. Deploy

### Post-Deployment
1. Verify health endpoint responds
2. Test authentication flow end-to-end
3. Test Stripe webhook with production keys
4. Configure Stripe webhook URL to production endpoint
5. Monitor error logs for first 24 hours

## Edge Cases
- Railway free tier limits — monitor usage, upgrade if needed
- Cold starts on Railway — acceptable for MVP, consider always-on for production
- Database migration fails — rollback procedure documented
- Vercel build fails — check Node.js version and build output

## Validation Rules
- [ ] All environment variables set in production (no `.env.example` defaults)
- [ ] HTTPS enforced on all endpoints
- [ ] Database is PostgreSQL in production (not SQLite)
- [ ] Stripe webhook URL updated to production domain
- [ ] CORS only allows production frontend domain
- [ ] Error logging is active and alerts configured
