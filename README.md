# Crawler_1 — Streamlit Deployment Guide

This repository contains a small crawler (`crawler.py`) that writes weather forecasts to a local SQLite database (`sqlightdata.db`), and a Streamlit app (`streamlit_app.py`) that reads that database and displays temperature data per location.

This guide explains how to deploy the Streamlit app to Streamlit Community Cloud (https://streamlit.io/cloud) and notes considerations for running the crawler and data storage in a cloud environment.

## Quick checklist before deploying
- Ensure `streamlit_app.py` and `requirements.txt` are in the repository root.
- Confirm `requirements.txt` lists `streamlit`, `pandas`, and `requests` (already included).

## Important: SQLite and cloud runtime caveat

Streamlit Cloud (and most ephemeral cloud runtimes) resets the filesystem on deploy/restart and does not persist files produced at runtime across deploys. That means:

- If your app relies on `sqlightdata.db` being present in the repo, you must commit the DB file into the repository (not recommended).  
- Recommended approaches:
  1. Use an external persistent data store (Postgres, Redis, S3, etc.) and point both crawler and app to it.  
  2. Run the crawler as part of the app startup (fetch latest data on each run) — simple but slower and may hit rate limits.  
  3. Schedule a separate cloud job to run the crawler and save results to an external store or commit a small CSV to the repo (requires automation).  

Choose an option before deploying.

## Deploy to Streamlit Community Cloud (recommended)

1. Create a GitHub repository and push this project to it.

   Example commands (run from `D:\\school_work\\crawler_1`):

   ```powershell
   git init
   git add .
   git commit -m "chore: initial commit with crawler and streamlit app"
   # Create GitHub repo manually or with gh CLI, then add remote
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git branch -M main
   git push -u origin main
   ```

2. Go to https://share.streamlit.io/ and sign in with GitHub.
3. Click **New app** → choose the repo, branch (`main`) and the file path `streamlit_app.py` → Deploy.

Notes:
- If the app needs persistent data, use environment variables and credentials in the Streamlit Cloud dashboard to point your app to an external DB or object storage.
- If you prefer the app to load fresh data on each start, modify `streamlit_app.py` to call the crawl endpoint or run the fetch logic at startup (be mindful of API keys and rate limits).

## Alternative: Deploy to other hosts (Docker)

If you want more control (and to run both crawler and web app), consider building a Docker image and deploying to a platform like Render, Fly, or a VPS.

Example `Dockerfile` (optional):

```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
```

Then build and push to your chosen provider.

## Environment variables & secrets
- If you use external services (proxy providers, Postgres, S3), configure credentials via the Streamlit Cloud **Secrets** UI or your host's secrets manager.

## CI / Automation (optional)
- You can add a GitHub Action to run the crawler on a schedule and push results to an external DB or commit a CSV to the repo (if small).

## Next steps I can help with
- Create a Dockerfile and test build.  
- Add a simple `docker-compose.yml` to run crawler + app + Postgres locally for testing.  
- Create a GitHub Actions workflow to run the crawler daily and store results in a remote DB or S3.  

Tell me which option you prefer and I will prepare the necessary files or commands.
