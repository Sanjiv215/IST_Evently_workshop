# EventHub &bull; Production Architecture

A full-stack event registration platform designed for a distributed multi-cloud architecture:
- **Frontend**: Hosted on **Vercel** (Static SPA with dynamic backend connectivity)
- **Backend API**: Hosted on **Render** (Flask + Gunicorn WSGI + CORS)
- **Database**: Hosted on **Supabase** (PostgreSQL)

---

## Architecture Overview

```
                      ┌──────────────────────┐
                      │    Vercel Frontend   │
                      │   (public/index.html)│
                      └──────────┬───────────┘
                                 │
                     HTTP / CORS │ Headers: X-User-Id
                                 ▼
                      ┌──────────────────────┐
                      │    Render Backend    │
                      │    (Flask / app.py)  │
                      └──────────┬───────────┘
                                 │
                     REST / SSL  │ Supabase Python SDK
                                 ▼
                      ┌──────────────────────┐
                      │  Supabase Database   │
                      │     (PostgreSQL)     │
                      └──────────────────────┘
```

---

## 1. Deploying the Backend on Render

1. Log in to [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** &rarr; **Web Service**.
3. Connect your GitHub repository.
4. Set the following build and start commands:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
5. In the **Environment Variables** section, add:
   - `SUPABASE_URL` = *(Your Supabase project URL)*
   - `SUPABASE_KEY` = *(Your Supabase publishable/anon key)*
   - `PYTHON_VERSION` = `3.11.9`
6. Click **Deploy Web Service**.
7. Once deployed, copy your Render service URL (e.g., `https://eventhub-backend.onrender.com`).

---

## 2. Deploying the Frontend on Vercel

1. Log in to [Vercel Dashboard](https://vercel.com/).
2. Click **Add New...** &rarr; **Project**.
3. Import your GitHub repository.
4. In **Project Settings**:
   - **Framework Preset**: `Other`
   - **Root Directory**: `./` (or `public`)
   - **Output Directory**: `public`
5. Click **Deploy**.
6. When your site is live on Vercel:
   - Open your Vercel URL (e.g., `https://eventhub.vercel.app`).
   - Use the **🌐 Render Backend API** bar at the top to paste your Render URL and click **Save & Connect**.
   - *(Optional)*: You can also set `window.API_BASE_URL = "https://your-backend.onrender.com"` in `public/config.js` and push to GitHub for automated zero-configuration deployments.

---

## 3. Local Development

### Run Backend
```bash
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Backend runs on `http://127.0.0.1:5001`.

### Open Frontend
Open `http://127.0.0.1:5001/` in your browser.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Healthcheck endpoint for Render |
| `GET` | `/api/events` | Browse all events |
| `GET` | `/api/events/<id>` | Event details |
| `POST` | `/api/registrations` | Create registration (receives `X-User-Id` header) |
| `GET` | `/api/me/registrations` | Current user registrations |
| `GET` | `/api/events/<id>/registrations` | Attendee list for an event |
| `GET` | `/docs` | Interactive Swagger-style documentation |

---

## Security & Pre-commit Hooks

This project is configured with **Husky** and **Gitleaks** to prevent secret exposure before committing:
```bash
npm install
```
Any accidental commit of API keys or credentials in tracked files will be intercepted and blocked automatically.
