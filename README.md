# EventHub &bull; Project Directory Structure

A full-stack event registration platform cleanly divided into `client` (frontend) and `server` (backend).

---

## Directory Layout

```
new1/
├── client/                     # Frontend Application (Vercel)
│   ├── public/                 # Static assets & index.html
│   │   └── index.html
│   ├── api/                    # Vercel Serverless API Proxy
│   │   └── [...path].js        # Forwards /api/* to Render backend securely
│   ├── index.html              # Frontend entrypoint
│   ├── package.json            # Client package config
│   ├── vercel.json             # Vercel deployment configuration
│   └── .vercelignore           # Ignored files for Vercel
│
├── server/                     # Backend API Service (Render)
│   ├── app.py                  # Flask REST API with Supabase
│   ├── requirements.txt        # Python backend dependencies
│   ├── render.yaml             # Render deployment configuration
│   ├── .env.example            # Backend environment variables template
│   └── templates/              # Server-rendered HTML fallback
│       └── index.html
│
├── .gitignore                  # Git ignore rules (protects all .env files)
├── .husky/                     # Pre-commit security hook (Gitleaks)
├── package.json                # Root package configuration
├── render.yaml                 # Root Render configuration
├── vercel.json                 # Root Vercel configuration
└── README.md                   # Project documentation
```

---

## 1. Deploying Frontend to Vercel

1. In [Vercel](https://vercel.com/), import your repository `Sanjiv215/IST_Evently_workshop`.
2. **Root Directory**: Select `client` (or leave default `./`).
3. Under **Environment Variables**, add:
   - `RENDER_BACKEND` = `https://<your-render-service>.onrender.com` *(or `BACKEND_URL`)*
4. Click **Deploy**.

---

## 2. Deploying Backend to Render

1. In [Render](https://dashboard.render.com/), create a new **Web Service**.
2. Select your repository `Sanjiv215/IST_Evently_workshop`.
3. Configure:
   - **Root Directory**: `server`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
4. Under **Environment Variables**, add:
   - `SUPABASE_URL` = *(Your Supabase URL)*
   - `SUPABASE_KEY` = *(Your Supabase Key)*
   - `PYTHON_VERSION` = `3.11.9`
5. Click **Deploy**.

---

## 3. Local Development

### Run Backend Server
```bash
# Option 1: From server directory
cd server
python app.py

# Option 2: From project root
python app.py
```
Backend runs at `http://127.0.0.1:5001`.

### Open Frontend
Open `http://127.0.0.1:5001/` in your browser.

---

## API Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/health` | Service healthcheck | No |
| `POST` | `/api/auth/login` | Sign in with email | No |
| `POST` | `/api/auth/signup` | Create user account | No |
| `GET` | `/api/auth/me` | Current user profile | Yes |
| `GET` | `/api/events` | Browse events | No |
| `GET` | `/api/events/<id>` | Event details | No |
| `POST` | `/api/registrations` | Register for an event | **Yes** (Bearer Token / X-User-Id) |
| `GET` | `/api/me/registrations` | View my registrations | **Yes** (Bearer Token / X-User-Id) |
| `GET` | `/api/events/<id>/registrations` | View attendee list | **Yes** (Owning Organizer only) |
| `GET` | `/docs` | Interactive Swagger API docs | No |
