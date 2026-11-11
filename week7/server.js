const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");

const courses = [
  { code: "DMD401", name: "互動設計實務", teacher: "陳思妤", dept: "數位媒體系", credit: 3 },
  { code: "DMD415", name: "數位內容企劃", teacher: "張立安", dept: "數位媒體系", credit: 2 },
  { code: "DMD428", name: "沉浸式媒體設計", teacher: "許家豪", dept: "數位媒體系", credit: 3 },
  { code: "GE210", name: "島嶼文化與永續", teacher: "周怡君", dept: "通識教育中心", credit: 2 },
  { code: "GE318", name: "跨文化溝通", teacher: "楊子萱", dept: "通識教育中心", credit: 2 }
];

const contentTypes = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8"
};

function getContentType(filePath) {
  return contentTypes[path.extname(filePath)] || "application/octet-stream";
}

function filterCourses(query = "", department = "all") {
  const keyword = query.trim().toLowerCase();
  return courses.filter((course) => {
    const searchable = `${course.code}${course.name}${course.teacher}`.toLowerCase();
    return searchable.includes(keyword) && (department === "all" || course.dept === department);
  });
}

function validateCredentials(account, password) {
  return account === "S112345678" && password === "demo1234";
}

function resolveStaticPath(rootDir, pathname) {
  const requested = pathname === "/" ? "index.html" : decodeURIComponent(pathname).replace(/^[/\\]+/, "");
  const resolved = path.resolve(rootDir, requested);
  const relative = path.relative(rootDir, resolved);
  if (relative.startsWith("..") || path.isAbsolute(relative)) return null;
  return resolved;
}

function sendJson(response, statusCode, payload) {
  response.writeHead(statusCode, { "Content-Type": "application/json; charset=utf-8" });
  response.end(JSON.stringify(payload));
}

function readJson(request) {
  return new Promise((resolve, reject) => {
    let body = "";
    request.on("data", (chunk) => { body += chunk; });
    request.on("end", () => {
      try { resolve(JSON.parse(body || "{}")); } catch (error) { reject(error); }
    });
    request.on("error", reject);
  });
}

function createRequestHandler(rootDir = __dirname) {
  return async (request, response) => {
    const url = new URL(request.url, `http://${request.headers.host || "localhost"}`);

    if (request.method === "GET" && url.pathname === "/api/health") {
      sendJson(response, 200, { status: "ok", service: "island-university-portal" });
      return;
    }

    if (request.method === "GET" && url.pathname === "/api/courses") {
      sendJson(response, 200, { courses: filterCourses(url.searchParams.get("q") || "", url.searchParams.get("dept") || "all") });
      return;
    }

    if (request.method === "POST" && url.pathname === "/api/login") {
      try {
        const { account, password } = await readJson(request);
        if (!validateCredentials(account, password)) {
          sendJson(response, 401, { success: false, message: "帳號或密碼錯誤" });
          return;
        }
        sendJson(response, 200, { success: true, student: { id: account, name: "林子晴" } });
      } catch {
        sendJson(response, 400, { success: false, message: "JSON 格式錯誤" });
      }
      return;
    }

    if (request.method !== "GET") {
      sendJson(response, 405, { error: "Method Not Allowed" });
      return;
    }

    const filePath = resolveStaticPath(rootDir, url.pathname);
    if (!filePath) {
      response.writeHead(403, { "Content-Type": "text/plain; charset=utf-8" });
      response.end("Forbidden");
      return;
    }

    fs.readFile(filePath, (error, data) => {
      if (error) {
        response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
        response.end("找不到檔案");
        return;
      }
      response.writeHead(200, { "Content-Type": getContentType(filePath) });
      response.end(data);
    });
  };
}

function createAppServer(options = {}) {
  return http.createServer(createRequestHandler(options.rootDir || __dirname));
}

if (require.main === module) {
  const host = "127.0.0.1";
  const port = Number(process.env.PORT) || 4173;
  createAppServer().listen(port, host, () => console.log(`校務系統已啟動：http://${host}:${port}`));
}

module.exports = { courses, createAppServer, createRequestHandler, filterCourses, getContentType, resolveStaticPath, validateCredentials };
