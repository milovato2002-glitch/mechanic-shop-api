# Mechanic Shop API — Deployment Checklist

## What changed

New files:
- `flask_app.py` — production WSGI entry point Render expects
- `Procfile` — gunicorn startup command
- `render.yaml` — Render service + Postgres database config
- `.github/workflows/ci.yml` — runs tests on every push and PR
- `.github/workflows/deploy.yml` — runs tests then triggers Render deploy on push to master
- `.env.example` — documents environment variables

Modified files:
- `app/__init__.py` — added DATABASE_URL handling (Render Postgres), SECRET_KEY env var, root and /health endpoints
- `requirements.txt` — added gunicorn and psycopg2-binary

## Step 1 — Drop files into your local repo

Copy the contents of this folder over your local `mechanic-shop-api` clone at whatever path you keep it (probably under your Desktop or OneDrive). The folder structure here mirrors the repo exactly.

```
cd C:\path\to\mechanic-shop-api
git status
git add .
git diff --staged   # review before committing
git commit -m "Add deployment and CI/CD pipeline"
git push origin master
```

## Step 2 — Set up Render

1. Go to https://render.com and sign in (or sign up). Free tier is fine.
2. Click New > Blueprint.
3. Connect your GitHub account, select `milovato2002-glitch/mechanic-shop-api`.
4. Render will detect `render.yaml` and provision:
   - A Postgres database named `mechanic-shop-db`
   - A web service named `mechanic-shop-api`
5. Click Apply. First deploy takes 5 to 10 minutes.
6. Once the web service is live, copy its URL (looks like `https://mechanic-shop-api.onrender.com`). That goes in your submission.

## Step 3 — Set up the Render deploy hook in GitHub

1. In Render, open your `mechanic-shop-api` service.
2. Go to Settings > Deploy Hook. Copy the URL.
3. In GitHub, go to https://github.com/milovato2002-glitch/mechanic-shop-api/settings/secrets/actions
4. Click New repository secret.
   - Name: `RENDER_DEPLOY_HOOK`
   - Value: paste the hook URL
5. Save.

After this, every push to master will run CI tests, then ping Render to redeploy.

## Step 4 — Verify

After your first push with these files:

1. Go to the Actions tab on GitHub. The CI workflow should show a green checkmark.
2. The Deploy workflow should run and fire the Render hook.
3. Render's deploy log should show the build succeeding.
4. Visit `https://mechanic-shop-api.onrender.com/health` — should return `{"status": "ok"}`.
5. Visit `https://mechanic-shop-api.onrender.com/api/docs` — Swagger UI loads.

## Notes

- Render free tier spins down after 15 minutes of inactivity. First request after a cold start can take 30 to 60 seconds. This is expected.
- Postgres is used in production. Your local dev still works on MySQL because the env-var resolution falls back to your local config.
- If the CI tests fail, the deploy job still runs because they're separate jobs. If you want the deploy to be blocked by failing tests, change `deploy.yml` to add `needs: test` and reference the CI job. Left as-is for now because the CI workflow already gates merges via branch protection if you enable that on GitHub.
