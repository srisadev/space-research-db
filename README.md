# Space Research Organization DB
## Flask + PostgreSQL — Cloud Deployment Guide

---

## Step 1 — Set up the database on Neon.tech (free)

1. Go to https://neon.tech and sign up for free
2. Click "New Project" → name it "space-research-db"
3. Click "SQL Editor" in the left sidebar
4. Copy and paste the entire contents of `schema.sql` and click Run
5. All 10 tables will be created with sample data
6. Click "Dashboard" → find the "Connection string" — it looks like:
   ```
   postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/neondb
   ```
   Copy this — you'll need it in Step 3.

---

## Step 2 — Push code to GitHub

1. Go to https://github.com and create a new repository called "space-research-db"
2. Make it Public
3. Upload all files from this folder to the repository

---

## Step 3 — Deploy on Render.com (free)

1. Go to https://render.com and sign up with your GitHub account
2. Click "New" → "Web Service"
3. Connect your GitHub repo "space-research-db"
4. Fill in:
   - Name: space-research-db
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Click "Environment Variables" → Add:
   - Key:   `DATABASE_URL`
   - Value: (paste the connection string from Neon.tech)
6. Click "Create Web Service"
7. Wait 2-3 minutes for it to deploy
8. You get a link like: `https://space-research-db.onrender.com`

---

## Share that link with your teacher. Done!
