# 🍱 The Food Palace

A full-featured restaurant ordering web application built with Flask & Supabase.

## Features
- 📋 Digital Menu with categories, veg/non-veg tags, and search
- 🛒 Pre-book orders with 50% advance UPI payment
- 🏪 Book at stall (instant order, pay at counter)
- 📊 Admin dashboard with sales reports & charts
- 🔒 Shop open/close toggle
- 📱 Mobile-optimized design
- ☁️ Supabase PostgreSQL cloud database

## Tech Stack
- **Backend**: Flask, SQLAlchemy
- **Database**: Supabase (PostgreSQL)
- **Frontend**: Tailwind CSS, Material Icons
- **Deployment**: Vercel

---

## 🚀 Deployment to Vercel

### Step 1: Push to GitHub
1. Create a new repository on [GitHub](https://github.com/new)
2. Upload all files from this folder to the repository
3. **IMPORTANT**: Do NOT upload the `.env` file (it contains secrets)

### Step 2: Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click **"Add New Project"** → Import your GitHub repository
3. Set **Framework Preset** to `Other`
4. Add these **Environment Variables** in Vercel's settings:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | `dev-secret-key-streetbite` |
| `DATABASE_URL` | `postgresql://postgres.apdqbeaglgbftfpmklrn:yashichitranshA1@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres` |
| `FLASK_ENV` | `production` |

5. Click **Deploy**!

### Step 3: Initialize Database (already done)
The database tables are already created on Supabase. Default admin login:
- **Username**: `admin`
- **Password**: `admin-password-123`

---

## 🔧 Local Development
```bash
pip install -r requirements.txt
python run.py
```
App runs at `http://localhost:3001`

## 📁 Project Structure
```
├── app/
│   ├── blueprints/
│   │   ├── admin/     # Admin dashboard, orders, settings
│   │   ├── auth/      # Login/logout
│   │   └── public/    # Menu, checkout, landing page
│   ├── templates/     # Jinja2 HTML templates
│   ├── static/        # CSS, JS, uploads
│   ├── services/      # Image handling
│   ├── extensions.py  # DB, Login, CSRF
│   └── models.py      # Database models
├── config.py          # App configuration
├── run.py             # Entry point
├── vercel.json        # Vercel deployment config
└── requirements.txt   # Python dependencies
```
