import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from supabase import create_client, Client, PostgrestAPIError
from dotenv import load_dotenv

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    allow_headers=["Content-Type", "Authorization", "X-User-Id", "Accept"],
    supports_credentials=True
)

supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

REG_TABLE = "registrations"


def get_reg_table():
    global REG_TABLE
    try:
        supabase.table("registrations").select("id").limit(0).execute()
        REG_TABLE = "registrations"
    except Exception:
        REG_TABLE = "registeration"
    return REG_TABLE


get_reg_table()


def get_authenticated_user():
    """Extract authenticated user from Authorization header, X-User-Id, or request params."""
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header:
        token = auth_header.replace("Bearer ", "").strip()

    user_id = request.headers.get("X-User-Id") or token or request.args.get("user_id")
    user_email = request.headers.get("X-User-Email")

    if not user_id and not user_email:
        if request.is_json and request.json:
            user_id = request.json.get("user_id")

    if not user_id and not user_email:
        return None

    # Check Supabase JWT if token has 3 parts
    if token and token.count(".") == 2:
        try:
            auth_user = supabase.auth.get_user(token)
            if auth_user and auth_user.user:
                user_id = auth_user.user.id
        except Exception:
            pass

    try:
        query = supabase.table("users").select("*")
        if user_id:
            res = query.eq("id", user_id).execute()
        elif user_email:
            res = query.eq("email", user_email).execute()
        else:
            return None

        if res.data and len(res.data) > 0:
            return res.data[0]

        if user_id:
            return {"id": user_id, "role": "student"}
    except Exception:
        if user_id:
            return {"id": user_id, "role": "student"}

    return None


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/")
def home():
    if request.headers.get("Accept") == "application/json":
        return jsonify({
            "title": "Event Registration API",
            "endpoints": [
                {"method": "POST", "path": "/api/auth/login", "description": "Sign in with email"},
                {"method": "POST", "path": "/api/auth/signup", "description": "Create a new user account"},
                {"method": "GET", "path": "/api/auth/me", "description": "Get current authenticated user"},
                {"method": "GET", "path": "/api/events", "description": "Browse events (public)"},
                {"method": "GET", "path": "/api/events/<event_id>", "description": "Event details (public)"},
                {"method": "POST", "path": "/api/registrations", "description": "Create registration (auth required, 201 or 409)"},
                {"method": "GET", "path": "/api/me/registrations", "description": "Current user registrations (auth required)"},
                {"method": "GET", "path": "/api/events/<event_id>/registrations", "description": "Attendee list (owning organizer only)"}
            ]
        })
    return render_template("index.html")


@app.route("/docs")
def docs():
    if request.headers.get("Accept") == "application/json":
        return jsonify({
            "title": "Event Registration API",
            "endpoints": [
                {"method": "POST", "path": "/api/auth/login", "description": "Sign in with email"},
                {"method": "POST", "path": "/api/auth/signup", "description": "Create a new user account"},
                {"method": "GET", "path": "/api/auth/me", "description": "Get current authenticated user"},
                {"method": "GET", "path": "/api/events", "description": "Browse events (public)"},
                {"method": "GET", "path": "/api/events/<event_id>", "description": "Event details (public)"},
                {"method": "POST", "path": "/api/registrations", "description": "Create registration (auth required, 201 or 409)"},
                {"method": "GET", "path": "/api/me/registrations", "description": "Current user registrations (auth required)"},
                {"method": "GET", "path": "/api/events/<event_id>/registrations", "description": "Attendee list (owning organizer only)"}
            ]
        })

    sample_event_id = "395fd854-3be2-4fa7-9993-0d1e735e4388"
    try:
        ev_res = supabase.table("events").select("id").limit(1).execute()
        if ev_res.data:
            sample_event_id = ev_res.data[0]["id"]
    except Exception:
        pass

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Event Registration API Docs</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0f172a;
            color: #e2e8f0;
            margin: 0;
            padding: 30px 20px;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #38bdf8; margin-bottom: 8px; font-size: 28px; }}
        p.subtitle {{ color: #94a3b8; margin-top: 0; margin-bottom: 24px; }}
        .card {{
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            margin-bottom: 16px;
            overflow: hidden;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);
        }}
        .card-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px 18px;
            background: #243248;
            border-bottom: 1px solid #334155;
        }}
        .badge {{
            font-weight: 700;
            font-size: 13px;
            padding: 4px 10px;
            border-radius: 6px;
            letter-spacing: 0.5px;
        }}
        .badge-get {{ background-color: #065f46; color: #34d399; }}
        .badge-post {{ background-color: #1e40af; color: #60a5fa; }}
        .endpoint-path {{
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: 15px;
            color: #f8fafc;
            text-decoration: none;
        }}
        .card-body {{ padding: 14px 18px; font-size: 14px; color: #cbd5e1; }}
        .desc {{ margin-top: 0; margin-bottom: 8px; font-weight: 500; }}
        pre {{
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 10px 14px;
            margin: 6px 0 0 0;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: 13px;
            color: #a5f3fc;
            overflow-x: auto;
        }}
        .btn {{
            display: inline-block;
            background: #0284c7;
            color: white;
            text-decoration: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 8px;
        }}
        .btn:hover {{ background: #0369a1; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Event Registration API Contract</h1>
        <p class="subtitle">API Documentation & Endpoint Specification (Authentication Enforced)</p>

        <!-- Auth Endpoints -->
        <div class="card">
            <div class="card-header">
                <span class="badge badge-post">POST</span>
                <span class="endpoint-path">/api/auth/login</span>
            </div>
            <div class="card-body">
                <p class="desc">Sign in with email.</p>
                <strong>JSON Request Body:</strong>
                <pre>{{\n  "email": "hemant.sharma@intellipaat.com"\n}}</pre>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="badge badge-post">POST</span>
                <span class="endpoint-path">/api/auth/signup</span>
            </div>
            <div class="card-body">
                <p class="desc">Create a new user account.</p>
                <strong>JSON Request Body:</strong>
                <pre>{{\n  "email": "student@example.com",\n  "role": "student"\n}}</pre>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="badge badge-get">GET</span>
                <a class="endpoint-path" href="/api/events" target="_blank">/api/events</a>
            </div>
            <div class="card-body">
                <p class="desc">Browse events (Public).</p>
                <a class="btn" href="/api/events" target="_blank">Test in Browser &rarr;</a>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="badge badge-get">GET</span>
                <a class="endpoint-path" href="/api/events/{sample_event_id}" target="_blank">/api/events/&lt;id&gt;</a>
            </div>
            <div class="card-body">
                <p class="desc">Event details (Public).</p>
                <a class="btn" href="/api/events/{sample_event_id}" target="_blank">Test with Sample ID &rarr;</a>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="badge badge-post">POST</span>
                <span class="endpoint-path">/api/registrations</span>
            </div>
            <div class="card-body">
                <p class="desc">Create registration &mdash; <strong>🔒 Auth required</strong> (201 Created or 409 Conflict if duplicate/full).</p>
                <strong>Headers:</strong> <code>Authorization: Bearer &lt;token&gt;</code> or <code>X-User-Id: &lt;user_id&gt;</code>
                <pre>{{\n  "event_id": "{sample_event_id}"\n}}</pre>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="badge badge-get">GET</span>
                <span class="endpoint-path">/api/me/registrations</span>
            </div>
            <div class="card-body">
                <p class="desc">Current user's registrations &mdash; <strong>🔒 Auth required</strong>.</p>
                <strong>Headers:</strong> <code>Authorization: Bearer &lt;token&gt;</code> or <code>X-User-Id: &lt;user_id&gt;</code>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="badge badge-get">GET</span>
                <span class="endpoint-path">/api/events/&lt;id&gt;/registrations</span>
            </div>
            <div class="card-body">
                <p class="desc">Attendee list &mdash; <strong>🔒 Owning organizer only</strong> (returns 403 Forbidden if not the event owner).</p>
                <strong>Headers:</strong> <code>Authorization: Bearer &lt;organizer_token&gt;</code>
            </div>
        </div>
    </div>
</body>
</html>"""
    return html


# --- AUTHENTICATION ENDPOINTS ---

@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    user_id = data.get("user_id")

    if not email and not user_id:
        return jsonify({"error": "Email is required to sign in"}), 400

    try:
        query = supabase.table("users").select("*")
        if user_id:
            res = query.eq("id", user_id).execute()
        else:
            res = query.eq("email", email).execute()

        if not res.data:
            return jsonify({"error": "User not found. Please sign up."}), 404

        user = res.data[0]
        return jsonify({
            "message": "Signed in successfully",
            "user": user,
            "token": user["id"]
        }), 200
    except PostgrestAPIError as error:
        return jsonify({"error": error.message}), 500


@app.route("/api/auth/signup", methods=["POST"])
def auth_signup():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    role = (data.get("role") or "student").strip().lower()

    if not email:
        return jsonify({"error": "Email is required"}), 400

    if role not in ["student", "organizer"]:
        return jsonify({"error": "Role must be 'student' or 'organizer'"}), 400

    try:
        existing = supabase.table("users").select("*").eq("email", email).execute()
        if existing.data and len(existing.data) > 0:
            return jsonify({"error": "User with this email already exists"}), 409

        new_user_res = supabase.table("users").insert({
            "email": email,
            "role": role
        }).execute()

        if not new_user_res.data:
            return jsonify({"error": "Failed to create user"}), 500

        user = new_user_res.data[0]
        return jsonify({
            "message": "Account created successfully",
            "user": user,
            "token": user["id"]
        }), 201
    except PostgrestAPIError as error:
        return jsonify({"error": error.message}), 500


@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    user = get_authenticated_user()
    if not user:
        return jsonify({"error": "Unauthenticated"}), 401
    return jsonify({"user": user}), 200


# --- EVENT ENDPOINTS ---

# 1. GET /api/events - Browse events (Public)
@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        response = supabase.table("events").select("*").execute()
        return jsonify(response.data), 200
    except PostgrestAPIError as error:
        return jsonify({"error": error.message}), 500


# 2. GET /api/events/<event_id> - Event details (Public)
@app.route("/api/events/<event_id>", methods=["GET"])
def get_event(event_id):
    try:
        response = supabase.table("events").select("*").eq("id", event_id).execute()
        if not response.data:
            return jsonify({"error": "Event not found"}), 404
        return jsonify(response.data[0]), 200
    except PostgrestAPIError as error:
        if "invalid input syntax for type uuid" in error.message:
            return jsonify({"error": "Event not found"}), 404
        return jsonify({"error": error.message}), 500


# 3. POST /api/registrations - Create registration (🔒 Auth required, 201 or 409)
@app.route("/api/registrations", methods=["POST"])
def create_registration():
    user = get_authenticated_user()
    if not user:
        return jsonify({"error": "Authentication required. Please sign in to register."}), 401

    data = request.get_json(silent=True) or {}
    event_id = data.get("event_id")
    if not event_id:
        return jsonify({"error": "event_id is required"}), 400

    try:
        event_res = supabase.table("events").select("*").eq("id", event_id).execute()
        if not event_res.data:
            return jsonify({"error": "Event not found"}), 404
        event = event_res.data[0]

        # Check if already registered -> 409 Conflict
        existing = (
            supabase.table(REG_TABLE)
            .select("*")
            .eq("user_id", user["id"])
            .eq("event_id", event_id)
            .execute()
        )
        if existing.data and len(existing.data) > 0:
            return jsonify({"error": "Already registered for this event"}), 409

        # Check capacity -> 409 Conflict
        capacity = event.get("capacity")
        if capacity is not None:
            count_res = (
                supabase.table(REG_TABLE)
                .select("*", count="exact")
                .eq("event_id", event_id)
                .execute()
            )
            current_count = count_res.count if count_res.count is not None else len(count_res.data)
            if current_count >= capacity:
                return jsonify({"error": "Event is at full capacity"}), 409

        # Insert registration -> 201 Created
        new_reg = (
            supabase.table(REG_TABLE)
            .insert({"user_id": user["id"], "event_id": event_id})
            .execute()
        )
        result = new_reg.data[0] if new_reg.data else {"message": "Registration successful"}
        return jsonify(result), 201
    except PostgrestAPIError as error:
        return jsonify({"error": error.message}), 500


# 4. GET /api/me/registrations - Current user's registrations (🔒 Auth required)
@app.route("/api/me/registrations", methods=["GET"])
@app.route("/api/events/me/registrations", methods=["GET"])
def get_my_registrations():
    user = get_authenticated_user()
    if not user:
        return jsonify({"error": "Authentication required to view your registrations."}), 401

    try:
        regs = (
            supabase.table(REG_TABLE)
            .select("*")
            .eq("user_id", user["id"])
            .not_.is_("event_id", "null")
            .execute()
            .data
        )

        event_ids = [r["event_id"] for r in regs if r.get("event_id")]
        if event_ids:
            events_res = supabase.table("events").select("*").in_("id", event_ids).execute()
            events_by_id = {e["id"]: e for e in events_res.data}
            for r in regs:
                r["event"] = events_by_id.get(r["event_id"])

        return jsonify(regs), 200
    except PostgrestAPIError as error:
        if "invalid input syntax for type uuid" in error.message:
            return jsonify({"error": "Event not found"}), 404
        return jsonify({"error": error.message}), 500


# 5. GET /api/events/<event_id>/registrations - Attendee list (🔒 Owning organizer only)
@app.route("/api/events/<event_id>/registrations", methods=["GET"])
def get_event_registrations(event_id):
    user = get_authenticated_user()
    if not user:
        return jsonify({"error": "Authentication required to view attendee list."}), 401

    try:
        event_res = supabase.table("events").select("*").eq("id", event_id).execute()
        if not event_res.data:
            return jsonify({"error": "Event not found"}), 404
        event = event_res.data[0]

        # Verify owning organizer -> 403 Forbidden
        if event.get("organiser_id") != user.get("id"):
            return jsonify({
                "error": "Forbidden: Only the owning organizer can view registrations for this event."
            }), 403

        regs = (
            supabase.table(REG_TABLE)
            .select("*")
            .eq("event_id", event_id)
            .execute()
            .data
        )

        user_ids = [r["user_id"] for r in regs if r.get("user_id")]
        if user_ids:
            users_res = supabase.table("users").select("id, email, role").in_("id", user_ids).execute()
            users_by_id = {u["id"]: u for u in users_res.data}
            for r in regs:
                r["user"] = users_by_id.get(r["user_id"])

        return jsonify(regs), 200
    except PostgrestAPIError as error:
        if "invalid input syntax for type uuid" in error.message:
            return jsonify({"error": "Event not found"}), 404
        return jsonify({"error": error.message}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, port=port)
