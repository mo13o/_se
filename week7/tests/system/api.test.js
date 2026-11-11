const test = require("node:test");
const assert = require("node:assert/strict");
const { before, after } = require("node:test");
const { createAppServer } = require("../../server");

let server;
let baseUrl;
before(async () => {
  server = createAppServer();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});
after(async () => { await new Promise((resolve) => server.close(resolve)); });

test("GET /api/health 回傳健康狀態", async () => {
  const response = await fetch(`${baseUrl}/api/health`);
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { status: "ok", service: "island-university-portal" });
});

test("GET /api/courses 支援系所與關鍵字", async () => {
  const response = await fetch(`${baseUrl}/api/courses?dept=${encodeURIComponent("數位媒體系")}&q=${encodeURIComponent("設計")}`);
  const data = await response.json();
  assert.equal(response.status, 200);
  assert.equal(data.courses.length, 2);
  assert.ok(data.courses.every((course) => course.dept === "數位媒體系"));
});

test("POST /api/login 接受正確帳密", async () => {
  const response = await fetch(`${baseUrl}/api/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ account: "S112345678", password: "demo1234" }) });
  const data = await response.json();
  assert.equal(response.status, 200);
  assert.equal(data.success, true);
  assert.equal(data.student.name, "林子晴");
});

test("POST /api/login 拒絕錯誤密碼", async () => {
  const response = await fetch(`${baseUrl}/api/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ account: "S112345678", password: "wrong" }) });
  assert.equal(response.status, 401);
  assert.equal((await response.json()).success, false);
});

test("網站首頁可由真實 HTTP server 取得", async () => {
  const response = await fetch(`${baseUrl}/`);
  const html = await response.text();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type"), /text\/html/);
  assert.match(html, /校務行政資訊系統/);
});
