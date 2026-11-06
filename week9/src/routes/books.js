import { apiError, json } from "../http.js";

const SORT_SQL = {
  newest: "b.created_at DESC",
  price_asc: "b.price ASC, b.id ASC",
  price_desc: "b.price DESC, b.id ASC",
  title: "b.title COLLATE NOCASE ASC",
};

export async function listBooks(request, env) {
  const url = new URL(request.url);
  const query = (url.searchParams.get("q") || "").trim();
  const categoryId = Number.parseInt(url.searchParams.get("category") || "", 10);
  const sort = url.searchParams.get("sort") || "newest";
  const orderBy = SORT_SQL[sort] || SORT_SQL.newest;

  const conditions = ["b.is_active = 1"];
  const values = [];

  if (query) {
    conditions.push("(b.title LIKE ? ESCAPE '\\' OR b.author LIKE ? ESCAPE '\\')");
    const escaped = query.replaceAll("\\", "\\\\").replaceAll("%", "\\%").replaceAll("_", "\\_");
    values.push(`%${escaped}%`, `%${escaped}%`);
  }
  if (Number.isInteger(categoryId) && categoryId > 0) {
    conditions.push("b.category_id = ?");
    values.push(categoryId);
  }

  const sql = `
    SELECT b.id, b.title, b.author, b.publisher, b.isbn, b.category_id,
           c.name AS category_name, b.price, b.stock, b.description,
           b.image_url, b.created_at
    FROM books b
    JOIN categories c ON c.id = b.category_id
    WHERE ${conditions.join(" AND ")}
    ORDER BY ${orderBy}
  `;
  const result = await env.DB.prepare(sql).bind(...values).all();
  return json({ ok: true, books: result.results, count: result.results.length });
}

export async function getBook(env, idText) {
  const id = Number.parseInt(idText, 10);
  if (!Number.isInteger(id) || id < 1) return apiError("書籍編號格式不正確", 400);

  const book = await env.DB.prepare(`
    SELECT b.id, b.title, b.author, b.publisher, b.isbn, b.category_id,
           c.name AS category_name, b.price, b.stock, b.description,
           b.image_url, b.created_at
    FROM books b
    JOIN categories c ON c.id = b.category_id
    WHERE b.id = ? AND b.is_active = 1
  `).bind(id).first();

  return book ? json({ ok: true, book }) : apiError("找不到這本書", 404);
}
