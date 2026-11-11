const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const { filterCourses, getContentType, resolveStaticPath, validateCredentials } = require("../../server");

test("server 回傳正確的 Content-Type", () => {
  assert.equal(getContentType("index.html"), "text/html; charset=utf-8");
  assert.equal(getContentType("styles.css"), "text/css; charset=utf-8");
  assert.equal(getContentType("image.png"), "application/octet-stream");
});

test("server 阻擋網站根目錄外的路徑", () => {
  const root = path.resolve("site-root");
  assert.equal(resolveStaticPath(root, "/"), path.join(root, "index.html"));
  assert.equal(resolveStaticPath(root, "/styles.css"), path.join(root, "styles.css"));
  assert.equal(resolveStaticPath(root, "/../../secret.txt"), null);
});

test("server 能依關鍵字與系所篩選課程", () => {
  assert.equal(filterCourses("互動", "all").length, 1);
  assert.equal(filterCourses("", "通識教育中心").length, 2);
  assert.equal(filterCourses("不存在", "all").length, 0);
});

test("server 僅接受示範帳號密碼", () => {
  assert.equal(validateCredentials("S112345678", "demo1234"), true);
  assert.equal(validateCredentials("S112345678", "wrong"), false);
});
