import { apiError, json } from "./http.js";
import { getBook, listBooks } from "./routes/books.js";
import { listCategories } from "./routes/categories.js";
import { createOrder } from "./routes/orders.js";
import { createBook, deactivateBook, listAdminBooks, listOrders, login, logout, me, requireAdmin, updateBook } from "./routes/admin.js";

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    try {
      if (request.method === "GET" && url.pathname === "/api/health") {
        return json({ ok: true, service: "BookNest API" });
      }
      if (request.method === "GET" && url.pathname === "/api/books") {
        return listBooks(request, env);
      }
      const bookMatch = url.pathname.match(/^\/api\/books\/(\d+)$/);
      if (request.method === "GET" && bookMatch) {
        return getBook(env, bookMatch[1]);
      }
      if (request.method === "GET" && url.pathname === "/api/categories") {
        return listCategories(env);
      }
      if (request.method === "POST" && url.pathname === "/api/orders") {
        return createOrder(request, env);
      }
      if (request.method === "POST" && url.pathname === "/api/admin/login") return login(request, env);
      if (request.method === "POST" && url.pathname === "/api/admin/logout") return logout(request, env);
      if (request.method === "GET" && url.pathname === "/api/admin/me") return me(request, env);
      if (url.pathname.startsWith("/api/admin/")) {
        if (!await requireAdmin(request, env)) return apiError("管理員登入已失效", 401);
        if (request.method === "GET" && url.pathname === "/api/admin/books") return listAdminBooks(env);
        if (request.method === "GET" && url.pathname === "/api/admin/orders") return listOrders(env);
        if (request.method === "POST" && url.pathname === "/api/admin/books") return createBook(request, env);
        const adminBookMatch = url.pathname.match(/^\/api\/admin\/books\/(\d+)$/);
        if (adminBookMatch && request.method === "PUT") return updateBook(request, env, Number(adminBookMatch[1]));
        if (adminBookMatch && request.method === "DELETE") return deactivateBook(env, Number(adminBookMatch[1]));
      }
      if (url.pathname.startsWith("/api/")) {
        return apiError("找不到此 API 路徑", 404);
      }

      return env.ASSETS.fetch(request);
    } catch (error) {
      console.error("BookNest API error:", error);
      return apiError("伺服器發生錯誤，請稍後再試", 500);
    }
  },
};
