import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from supabase import create_client, Client, PostgrestAPIError
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Content-Type", "Authorization", "X-User-Id", "Accept"])

supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

REG_TABLE = "registrations"

DEFAULT_USER_ID = "7f2e9b9e-d9d8-4712-b6c3-6d2293a73c2a"


def get_reg_table():
    global REG_TABLE
    try:
        supabase.table("registrations").select("id").limit(0).execute()
        REG_TABLE = "registrations"
    except Exception:
        REG_TABLE = "registeration"
    return REG_TABLE


get_reg_table()


def get_user_id():
    """Retrieve user_id from X-User-Id header, query params, body, or fallback to default."""
    return (
        request.headers.get("X-User-Id")
        or request.args.get("user_id")
        or (request.json.get("user_id") if request.is_json and request.json else None)
        or DEFAULT_USER_ID
    )


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/")
def home():
    if request.headers.get("Accept") == "application/json":
        return jsonify({
            "title": "Event Registration API",
            "endpoints": [
                {"method": "GET", "path": "/api/events", "description": "Browse events"},
                {"method": "GET", "path": "/api/events/<event_id>", "description": "Event details"},
                {"method": "POST", "path": "/api/registrations", "description": "Create registration (201 or 409)"},
                {"method": "GET", "path": "/api/me/registrations", "description": "Current user's registrations"},
                {"method": "GET", "path": "/api/events/<event_id>/registrations", "description": "Attendee list"}
            ]
        })
    return render_template("index.html")


@app.route("/docs")
def docs():
    if request.headers.get("Accept") == "application/json":
        return jsonify({
            "title": "Event Registration API",
            "endpoints": [
                {"method": "GET", "path": "/api/events", "description": "Browse events"},
                {"method": "GET", "path": "/api/events/<event_id>", "description": "Event details"},
                {"method": "POST", "path": "/api/registrations", "description": "Create registration (201 or 409)"},
                {"method": "GET", "path": "/api/me/registrations", "description": "Current user's registrations"},
                {"method": "GET", "path": "/api/events/<event_id>/registrations", "description": "Attendee list"}
            ]
        })

    # Fetch a sample event id dynamically for live links
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
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        h1 {{
            color: #38bdf8;
            margin-bottom: 8px;
            font-size: 28px;
        }}
        p.subtitle {{
            color: #94a3b8;
            margin-top: 0;
            margin-bottom: 24px;
        }}
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
        .badge-get {{
            background-color: #065f46;
            color: #34d399;
        }}
        .badge-post {{
            background-color: #1e40af;
            color: #60a5fa;
        }}
        .endpoint-path {{
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
            font-size: 15px;
            color: #f8fafc;
            text-decoration: none;
        }}
        .endpoint-path:hover {{
            text-decoration: underline;
            color: #38bdf8;
        }}
        .card-body {{
            padding: 14px 18px;
            font-size: 14px;
            color: #cbd5e1;
        }}
        .desc {{
            margin-top: 0;
            margin-bottom: 8px;
            font-weight: 500;
        }}
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
        .btn:hover {{
            background: #0369a1;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Event Registration API Contract</h1>
        <p class="subtitle">Interactive API Documentation & Endpoint Directory</p>

        <!-- 1. GET /api/events -->
        <div class="card">
            <div class="card-header">
                <span class="badge badge-get">GET</span>
                <a class="endpoint-path" href="/api/events" target="_blank">/api/events</a>
            </div>
            <div class="card-body">
                <p class="desc">Browse events.</p>
                <a class="btn" href="/api/events" target="_blank">Test in Browser &rarr;</a>
            </div>
        </div>

        <!-- 2. GET /api/events/<id> -->
        <div class="card">
            <div class="card-header">
                <span class="badge badge-get">GET</span>
                <a class="endpoint-path" href="/api/events/{sample_event_id}" target="_blank">/api/events/&lt;id&gt;</a>
            </div>
            <div class="card-body">
                <p class="desc">Event details.</p>
                <a class="btn" href="/api/events/{sample_event_id}" target="_blank">Test with Sample ID &rarr;</a>
            </div>
        </div>

        <!-- 3. POST /api/registrations -->
        <div class="card">
            <div class="card-header">
                <span class="badge badge-post">POST</span>
                <span class="endpoint-path">/api/registrations</span>
            </div>
            <div class="card-body">
                <p class="desc">Create registration (returns 201 Created or 409 Conflict if duplicate/full).</p>
                <strong>JSON Request Body:</strong>
                <pre>{{\n  "event_id": "{sample_event_id}",\n  "user_id": "7f2e9b9e-d9d8-4712-b6c3-6d2293a73c2a"\n}}</pre>
            </div>
        </div>

        <!-- 4. GET /api/me/registrations -->
        <div class="card">
            <div class="card-header">
                <span class="badge badge-get">GET</span>
                <a class="endpoint-path" href="/api/me/registrations?user_id={DEFAULT_USER_ID}" target="_blank">/api/me/registrations?user_id={DEFAULT_USER_ID}</a>
            </div>
            <div class="card-body">
                <p class="desc">Current user's registrations. Pass via <strong>X-User-Id header</strong> or <strong>?user_id= URL parameter</strong>.</p>
                <div style="margin-bottom: 8px;">
                    <a class="btn" href="/api/me/registrations?user_id={DEFAULT_USER_ID}" target="_blank">Test with URL Query (?user_id=...) &rarr;</a>
                    <button class="btn" style="background:#475569; cursor:pointer;" onclick="testWithHeader()">Test with X-User-Id Header (Fetch API)</button>
                </div>
                <pre id="header-result" style="display:none;"></pre>
                <script>
                    function testWithHeader() {{
                        fetch('/api/me/registrations', {{
                            headers: {{ 'X-User-Id': '{DEFAULT_USER_ID}' }}
                        }})
                        .then(r => r.json())
                        .then(data => {{
                            const pre = document.getElementById('header-result');
                            pre.style.display = 'block';
                            pre.textContent = JSON.stringify(data, null, 2);
                        }});
                    }}
                </script>
            </div>
        </div>

        <!-- 5. GET /api/events/<id>/registrations -->
        <div class="card">
            <div class="card-header">
                <span class="badge badge-get">GET</span>
                <a class="endpoint-path" href="/api/events/{sample_event_id}/registrations" target="_blank">/api/events/&lt;id&gt;/registrations</a>
            </div>
            <div class="card-body">
                <p class="desc">Attendee list for a specific event.</p>
                <a class="btn" href="/api/events/{sample_event_id}/registrations" target="_blank">Test with Sample ID &rarr;</a>
            </div>
        </div>
    </div>
</body>
</html>"""
    return html


# 1. GET /api/events - Browse events
@app.route("/api/events", methods=["GET"])
def get_events():
    try:
        response = supabase.table("events").select("*").execute()
        return jsonify(response.data), 200
    except PostgrestAPIError as error:
        return jsonify({"error": error.message}), 500


# 2. GET /api/events/<event_id> - Event details
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


# 3. POST /api/registrations - Create registration, 201 or 409 (no auth required)
@app.route("/api/registrations", methods=["POST"])
def create_registration():
    data = request.get_json(silent=True) or {}
    event_id = data.get("event_id")
    if not event_id:
        return jsonify({"error": "event_id is required"}), 400

    user_id = data.get("user_id") or get_user_id()

    try:
        event_res = supabase.table("events").select("*").eq("id", event_id).execute()
        if not event_res.data:
            return jsonify({"error": "Event not found"}), 404
        event = event_res.data[0]

        # Check if already registered -> 409 Conflict
        existing = (
            supabase.table(REG_TABLE)
            .select("*")
            .eq("user_id", user_id)
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
            .insert({"user_id": user_id, "event_id": event_id})
            .execute()
        )
        result = new_reg.data[0] if new_reg.data else {"message": "Registration successful"}
        return jsonify(result), 201
    except PostgrestAPIError as error:
        return jsonify({"error": error.message}), 500


# 4. GET /api/me/registrations - Current user's registrations (no auth required)
@app.route("/api/me/registrations", methods=["GET"])
@app.route("/api/events/me/registrations", methods=["GET"])
def get_my_registrations():
    user_id = get_user_id()

    try:
        regs = (
            supabase.table(REG_TABLE)
            .select("*")
            .eq("user_id", user_id)
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


# 5. GET /api/events/<event_id>/registrations - Attendee list (no auth required)
@app.route("/api/events/<event_id>/registrations", methods=["GET"])
def get_event_registrations(event_id):
    try:
        event_res = supabase.table("events").select("*").eq("id", event_id).execute()
        if not event_res.data:
            return jsonify({"error": "Event not found"}), 404

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
