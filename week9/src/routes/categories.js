import { json } from "../http.js";

export async function listCategories(env) {
  const result = await env.DB.prepare(`
    SELECT c.id, c.name, COUNT(b.id) AS book_count
    FROM categories c
    LEFT JOIN books b ON b.category_id = c.id AND b.is_active = 1
    GROUP BY c.id, c.name
    ORDER BY c.id ASC
  `).all();
  return json({ ok: true, categories: result.results });
}
