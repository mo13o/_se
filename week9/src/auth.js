const encoder = new TextEncoder();

function fromBase64(value) {
  return Uint8Array.from(atob(value), char => char.charCodeAt(0));
}
function toHex(bytes) {
  return [...new Uint8Array(bytes)].map(byte => byte.toString(16).padStart(2, "0")).join("");
}
async function sha256(value) {
  return toHex(await crypto.subtle.digest("SHA-256", encoder.encode(value)));
}
function readCookie(request, name) {
  const cookies = request.headers.get("cookie") || "";
  for (const part of cookies.split(";")) {
    const [key, ...rest] = part.trim().split("=");
    if (key === name) return rest.join("=");
  }
  return null;
}

export async function verifyPassword(password, storedHash) {
  const [scheme, roundsText, saltText, expectedText] = String(storedHash).split("$");
  const rounds = Number(roundsText);
  if (scheme !== "pbkdf2" || !Number.isInteger(rounds) || !saltText || !expectedText) return false;
  const key = await crypto.subtle.importKey("raw", encoder.encode(password), "PBKDF2", false, ["deriveBits"]);
  const actual = new Uint8Array(await crypto.subtle.deriveBits({ name: "PBKDF2", hash: "SHA-256", salt: fromBase64(saltText), iterations: rounds }, key, 256));
  const expected = fromBase64(expectedText);
  if (actual.length !== expected.length) return false;
  let difference = 0;
  for (let index = 0; index < actual.length; index++) difference |= actual[index] ^ expected[index];
  return difference === 0;
}

export async function createSession(env, adminId) {
  const token = `${crypto.randomUUID()}${crypto.randomUUID()}`;
  const tokenHash = await sha256(token);
  const expires = new Date(Date.now() + 8 * 60 * 60 * 1000);
  await env.DB.prepare("DELETE FROM admin_sessions WHERE expires_at <= strftime('%Y-%m-%dT%H:%M:%fZ', 'now')").run();
  await env.DB.prepare("INSERT INTO admin_sessions (admin_id, token_hash, expires_at) VALUES (?, ?, ?)").bind(adminId, tokenHash, expires.toISOString()).run();
  return { token, expires };
}

export async function getAdmin(request, env) {
  const token = readCookie(request, "booknest_admin");
  if (!token) return null;
  return env.DB.prepare(`SELECT a.id, a.username FROM admin_sessions s JOIN admins a ON a.id = s.admin_id WHERE s.token_hash = ? AND s.expires_at > strftime('%Y-%m-%dT%H:%M:%fZ', 'now')`).bind(await sha256(token)).first();
}

export async function deleteSession(request, env) {
  const token = readCookie(request, "booknest_admin");
  if (token) await env.DB.prepare("DELETE FROM admin_sessions WHERE token_hash = ?").bind(await sha256(token)).run();
}

export function sessionCookie(token, expires) {
  return `booknest_admin=${token}; Path=/; HttpOnly; SameSite=Strict; Expires=${expires.toUTCString()}`;
}
export const expiredSessionCookie = "booknest_admin=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0";
