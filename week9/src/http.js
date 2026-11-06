export function json(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      ...extraHeaders,
    },
  });
}

export function apiError(message, status = 400, details) {
  return json({ ok: false, error: message, ...(details ? { details } : {}) }, status);
}
