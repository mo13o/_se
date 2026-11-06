import { apiError, json } from "../http.js";
import { createSession, deleteSession, expiredSessionCookie, getAdmin, sessionCookie, verifyPassword } from "../auth.js";

export async function login(request, env) {
  let body;
  try { body = await request.json(); } catch { return apiError("登入資料格式不正確", 400); }
  const username = String(body.username || "").trim();
  const admin = await env.DB.prepare("SELECT id, username, password_hash FROM admins WHERE username = ?").bind(username).first();
  if (!admin || !await verifyPassword(String(body.password || ""), admin.password_hash)) return apiError("帳號或密碼不正確", 401);
  const session = await createSession(env, admin.id);
  return json({ ok: true, admin: { id: admin.id, username: admin.username } }, 200, { "set-cookie": sessionCookie(session.token, session.expires) });
}
export async function logout(request, env) {
  await deleteSession(request, env);
  return json({ ok: true }, 200, { "set-cookie": expiredSessionCookie });
}
export async function me(request, env) {
  const admin = await getAdmin(request, env);
  return admin ? json({ ok: true, admin }) : apiError("尚未登入", 401);
}
export async function requireAdmin(request, env) {
  return getAdmin(request, env);
}

function validateBook(body) {
  const book = {
    title: String(body.title || "").trim(), author: String(body.author || "").trim(),
    publisher: String(body.publisher || "").trim(), isbn: String(body.isbn || "").trim(),
    category_id: Number(body.category_id), price: Number(body.price), stock: Number(body.stock),
    description: String(body.description || "").trim(), image_url: String(body.image_url || "").trim(),
  };
  if (!book.title || !book.author || !book.publisher || !book.isbn) return null;
  if (!Number.isInteger(book.category_id) || book.category_id < 1 || !Number.isInteger(book.price) || book.price < 0 || !Number.isInteger(book.stock) || book.stock < 0) return null;
  return book;
}

export async function listAdminBooks(env) {
  const result = await env.DB.prepare(`SELECT b.*, c.name AS category_name FROM books b JOIN categories c ON c.id = b.category_id ORDER BY b.id DESC`).all();
  return json({ ok: true, books: result.results });
}
export async function createBook(request, env) {
  let body; try { body = await request.json(); } catch { return apiError("書籍資料格式不正確", 400); }
  const book = validateBook(body); if (!book) return apiError("請完整填寫書籍資料", 400);
  try {
    const result = await env.DB.prepare(`INSERT INTO books (title, author, publisher, isbn, category_id, price, stock, description, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`).bind(...Object.values(book)).run();
    return json({ ok: true, id: result.meta.last_row_id }, 201);
  } catch (error) { return String(error).includes("UNIQUE") ? apiError("ISBN 已存在", 409) : Promise.reject(error); }
}
export async function updateBook(request, env, id) {
  let body; try { body = await request.json(); } catch { return apiError("書籍資料格式不正確", 400); }
  const book = validateBook(body); if (!book) return apiError("請完整填寫書籍資料", 400);
  try {
    const result = await env.DB.prepare(`UPDATE books SET title=?, author=?, publisher=?, isbn=?, category_id=?, price=?, stock=?, description=?, image_url=?, is_active=? WHERE id=?`).bind(...Object.values(book), body.is_active === false || Number(body.is_active) === 0 ? 0 : 1, id).run();
    return result.meta.changes ? json({ ok: true }) : apiError("找不到書籍", 404);
  } catch (error) { return String(error).includes("UNIQUE") ? apiError("ISBN 已存在", 409) : Promise.reject(error); }
}
export async function deactivateBook(env, id) {
  const result = await env.DB.prepare("UPDATE books SET is_active = 0 WHERE id = ?").bind(id).run();
  return result.meta.changes ? json({ ok: true }) : apiError("找不到書籍", 404);
}
export async function listOrders(env) {
  const result = await env.DB.prepare(`SELECT o.id, o.order_number, o.customer_name, o.customer_email, o.total_amount, o.status, o.created_at, COUNT(oi.id) AS item_count FROM orders o LEFT JOIN order_items oi ON oi.order_id=o.id GROUP BY o.id ORDER BY o.created_at DESC`).all();
  return json({ ok: true, orders: result.results });
}
