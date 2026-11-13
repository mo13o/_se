import test from "node:test";
import assert from "node:assert/strict";
import worker from "../src/index.js";
import { verifyPassword } from "../src/auth.js";

function createDb(rows = []) {
  return {
    prepare(sql) {
      return {
        bind(...values) {
          return {
            all: async () => ({ results: rows, sql, values }),
            first: async () => rows[0] || null,
          };
        },
        all: async () => ({ results: rows }),
      };
    },
  };
}

test("GET /api/health 回傳服務狀態", async () => {
  const response = await worker.fetch(new Request("http://localhost/api/health"), {});
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { ok: true, service: "BookNest API" });
});

test("GET /api/books 回傳書籍陣列", async () => {
  const response = await worker.fetch(new Request("http://localhost/api/books?q=SQL"), {
    DB: createDb([{ id: 1, title: "SQL 資料庫實務" }]),
  });
  const body = await response.json();
  assert.equal(response.status, 200);
  assert.equal(body.count, 1);
  assert.equal(body.books[0].title, "SQL 資料庫實務");
});

test("GET /api/books/:id 對不存在書籍回傳 404", async () => {
  const response = await worker.fetch(new Request("http://localhost/api/books/999"), {
    DB: createDb([]),
  });
  assert.equal(response.status, 404);
});

test("未知 API 回傳 JSON 404", async () => {
  const response = await worker.fetch(new Request("http://localhost/api/unknown"), {});
  assert.equal(response.status, 404);
  assert.equal((await response.json()).ok, false);
});

test("POST /api/orders 拒絕空白訂單", async () => {
  const response = await worker.fetch(new Request("http://localhost/api/orders", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({}),
  }), {});
  assert.equal(response.status, 400);
  assert.equal((await response.json()).ok, false);
});

test("未登入不能讀取管理員書籍 API", async () => {
  const response = await worker.fetch(new Request("http://localhost/api/admin/books"), {
    DB: createDb([]),
  });
  assert.equal(response.status, 401);
});

test("PBKDF2 管理員密碼驗證正確", async () => {
  const hash = "pbkdf2$210000$Csqzy1TSKsSkWUsKj0uYgg==$g4XkqIkGDSWlhbhg/538DFkftYJwhg6ONh3yY71EBtw=";
  assert.equal(await verifyPassword("BookNest123!", hash), true);
  assert.equal(await verifyPassword("wrong-password", hash), false);
});
