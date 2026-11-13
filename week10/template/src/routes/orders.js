import { apiError, json } from "../http.js";

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function normalizeItems(items) {
  if (!Array.isArray(items) || items.length === 0 || items.length > 30) return null;
  const quantities = new Map();
  for (const item of items) {
    const bookId = Number(item?.book_id);
    const quantity = Number(item?.quantity);
    if (!Number.isInteger(bookId) || bookId < 1 || !Number.isInteger(quantity) || quantity < 1 || quantity > 99) return null;
    quantities.set(bookId, (quantities.get(bookId) || 0) + quantity);
  }
  return [...quantities].map(([book_id, quantity]) => ({ book_id, quantity }));
}

export async function createOrder(request, env) {
  let body;
  try { body = await request.json(); } catch { return apiError("訂單資料格式不正確", 400); }
  const customerName = String(body.customer_name || "").trim();
  const customerEmail = String(body.customer_email || "").trim().toLowerCase();
  const clientOrderId = String(body.client_order_id || "").trim();
  const items = normalizeItems(body.items);
  if (!customerName || customerName.length > 100) return apiError("請填寫正確的訂購人姓名", 400);
  if (!EMAIL_PATTERN.test(customerEmail) || customerEmail.length > 254) return apiError("請填寫正確的電子郵件", 400);
  if (!/^[0-9a-f-]{36}$/i.test(clientOrderId)) return apiError("訂單識別碼格式不正確", 400);
  if (!items) return apiError("購買商品資料不正確", 400);

  const existing = await env.DB.prepare("SELECT id, order_number, total_amount, status, created_at FROM orders WHERE client_order_id = ?").bind(clientOrderId).first();
  if (existing) return json({ ok: true, order: existing, duplicate: true });

  const placeholders = items.map(() => "?").join(",");
  const result = await env.DB.prepare(`SELECT id, title, price, stock FROM books WHERE is_active = 1 AND id IN (${placeholders})`).bind(...items.map(item => item.book_id)).all();
  if (result.results.length !== items.length) return apiError("部分書籍不存在或已下架，請重新整理購物車", 409);
  const books = new Map(result.results.map(book => [book.id, book]));
  let totalAmount = 0;
  for (const item of items) {
    const book = books.get(item.book_id);
    if (book.stock < item.quantity) return apiError(`《${book.title}》庫存不足，目前只剩 ${book.stock} 本`, 409);
    totalAmount += book.price * item.quantity;
  }

  const orderNumber = `BN${Date.now().toString(36).toUpperCase()}${crypto.randomUUID().slice(0, 6).toUpperCase()}`;
  const statements = [env.DB.prepare("INSERT INTO orders (order_number, customer_name, customer_email, total_amount, status, client_order_id) VALUES (?, ?, ?, ?, 'pending', ?)").bind(orderNumber, customerName, customerEmail, totalAmount, clientOrderId)];
  for (const item of items) {
    const book = books.get(item.book_id);
    statements.push(env.DB.prepare("INSERT INTO order_items (order_id, book_id, quantity, unit_price) SELECT id, ?, ?, ? FROM orders WHERE order_number = ?").bind(item.book_id, item.quantity, book.price, orderNumber));
    statements.push(env.DB.prepare("UPDATE books SET stock = stock - ? WHERE id = ?").bind(item.quantity, item.book_id));
  }
  try {
    await env.DB.batch(statements);
  } catch (error) {
    console.error("Create order batch failed:", error);
    if (String(error).includes("CHECK constraint failed")) return apiError("商品庫存剛剛發生變動，請重新確認購物車", 409);
    if (String(error).includes("client_order_id")) {
      const duplicate = await env.DB.prepare("SELECT id, order_number, total_amount, status, created_at FROM orders WHERE client_order_id = ?").bind(clientOrderId).first();
      if (duplicate) return json({ ok: true, order: duplicate, duplicate: true });
    }
    throw error;
  }
  const order = await env.DB.prepare("SELECT id, order_number, customer_name, customer_email, total_amount, status, created_at FROM orders WHERE order_number = ?").bind(orderNumber).first();
  return json({ ok: true, order }, 201);
}
