export default async function handler(req, res) {
  const backendBase = (
    process.env.BACKEND_URL ||
    process.env.RENDER_BACKEND_URL ||
    process.env.RENDER_URL ||
    ""
  ).replace(/\/+$/, "");

  if (!backendBase) {
    return res.status(500).json({
      error: "BACKEND_URL is not set. Add BACKEND_URL in Vercel Project Settings -> Environment Variables."
    });
  }

  // Preserve request path and query string
  const requestPath = req.url || "";
  const targetUrl = `${backendBase}${requestPath.startsWith("/") ? "" : "/"}${requestPath}`;

  try {
    const headers = {};
    for (const [key, value] of Object.entries(req.headers)) {
      const lower = key.toLowerCase();
      if (lower !== "host" && lower !== "content-length") {
        headers[key] = value;
      }
    }

    const options = {
      method: req.method,
      headers: headers
    };

    if (req.method !== "GET" && req.method !== "HEAD" && req.body) {
      options.body = typeof req.body === "object" ? JSON.stringify(req.body) : req.body;
      if (!headers["content-type"]) {
        headers["content-type"] = "application/json";
      }
    }

    const response = await fetch(targetUrl, options);
    const contentType = response.headers.get("content-type") || "";

    res.status(response.status);

    if (contentType.includes("application/json")) {
      const data = await response.json();
      return res.json(data);
    } else {
      const text = await response.text();
      return res.send(text);
    }
  } catch (err) {
    return res.status(502).json({
      error: "Backend communication failed",
      details: err.message
    });
  }
}
