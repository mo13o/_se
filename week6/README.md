# Docker 微服務展示系統

本專案是一個可實際執行的 Docker Compose 練習，使用三個獨立服務組成簡易留言板：Nginx 提供靜態網頁並代理 API、Python Flask 處理商業邏輯、PostgreSQL 保存資料。

## 系統架構

```text
瀏覽器 http://localhost:8080
              │
              ▼
       Nginx（對外 port 8080）
          │             │
          │ /           └─ 靜態前端 HTML/CSS/JS
          │ /api/*
          ▼
       Flask API（內部 port 5000）
          │
          ▼
       PostgreSQL（內部 port 5432）
```

只有 Nginx 對主機公開連接埠。API 和資料庫只存在 Compose 內部網路，服務彼此以名稱 `api`、`db` 連線。

## 專案內容

```text
.
├── docker-compose.yml          # 定義並串接三個容器
├── backend/
│   ├── Dockerfile              # 建置 Flask API 映像
│   ├── requirements.txt
│   └── app.py
├── database/
│   └── init.sql                # 第一次建立資料庫時初始化資料表
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
└── nginx/
    └── default.conf            # 靜態檔案與反向代理設定
```

## 環境需求

- Docker Desktop
- Docker Compose v2（Docker Desktop 已內含）
- Windows 建議啟用 WSL 2 backend

確認安裝：

```powershell
docker --version
docker compose version
```

## 啟動方式

在本 README 所在目錄開啟終端機：

```powershell
docker compose up --build -d
```

等待所有容器健康後，開啟 <http://localhost:8080>。網頁可以讀取及新增留言，資料會保存在 PostgreSQL volume 中。

檢查服務狀態與紀錄：

```powershell
docker compose ps
docker compose logs -f
```

直接測試 API：

```powershell
curl.exe http://localhost:8080/api/health
curl.exe http://localhost:8080/api/messages
```

停止容器但保留資料：

```powershell
docker compose down
```

停止容器並刪除資料庫 volume（資料會消失）：

```powershell
docker compose down -v
```

## Docker 學習與實作紀錄

### 1. Image 與 Container

- **Image（映像）**是唯讀的應用程式範本，例如 `nginx:1.27-alpine`、`postgres:16-alpine`。
- **Container（容器）**是映像執行後的實例。刪除容器不等於刪除映像。
- `docker build` 依 Dockerfile 建立映像；`docker run` 從映像建立並啟動容器。

本專案的 `api` 由 `backend/Dockerfile` 自行建置；`nginx` 與 `db` 使用官方映像。

### 2. Dockerfile

本專案 Dockerfile 的重點：

- `FROM python:3.12-slim`：選擇基礎映像。
- `WORKDIR /app`：設定容器內工作目錄。
- 先複製並安裝 `requirements.txt`，可利用建置快取。
- `COPY app.py .`：把程式加入映像。
- `CMD [...]`：以 Gunicorn 啟動服務。

重新建置 API：

```powershell
docker compose build api
```

### 3. Docker Compose

Compose 讓多個容器以一份 YAML 管理。本專案定義：

- `nginx`：入口、靜態 Web Server、Reverse Proxy。
- `api`：Python Flask REST API。
- `db`：PostgreSQL 資料庫。

`depends_on` 搭配 health check，讓 API 等資料庫健康後啟動，Nginx 再等 API 健康。

### 4. Network 與 Reverse Proxy

Compose 會自動建立預設網路及內部 DNS，因此 Nginx 使用 `http://api:5000` 找到 API，API 使用主機名稱 `db` 找到 PostgreSQL。使用者只需連線 Nginx 的 `8080` port。

`ports: "8080:80"` 表示：

```text
主機的 8080 port → 容器的 80 port
```

### 5. Volume 與資料持久化

容器可以隨時重建，因此重要資料不能只放在容器可寫層。`postgres_data` 是 named volume，掛載在 PostgreSQL 資料目錄。執行一般的 `docker compose down` 後資料仍存在；加上 `-v` 才會一併刪除。

查看 volume：

```powershell
docker volume ls
```

### 6. Bind Mount

Nginx 設定和前端檔案使用 bind mount，以唯讀的 `:ro` 掛載進容器。修改前端後通常重新整理瀏覽器即可看見結果，不必重建映像。

### 7. 常用除錯指令

```powershell
# 列出本專案容器
docker compose ps

# 顯示特定服務紀錄
docker compose logs api
docker compose logs db
docker compose logs nginx

# 進入 API 容器
docker compose exec api sh

# 在資料庫執行 SQL
docker compose exec db psql -U demo_user -d docker_demo

# 查看所有容器與映像
docker ps -a
docker images
```

## API 規格

| 方法 | 路徑 | 功能 |
|---|---|---|
| `GET` | `/api/health` | 檢查 API 與資料庫連線 |
| `GET` | `/api/messages` | 取得最近 20 筆留言 |
| `POST` | `/api/messages` | 新增留言，JSON 格式為 `{ "content": "文字" }` |

## 實作成果與觀察

- 將 Web、API、Database 分成獨立容器，任一服務皆可單獨替換或擴充。
- 透過 Nginx 統一入口，前端不需要知道 API 容器實際位置。
- PostgreSQL 不公開至主機，降低不必要的外部存取面。
- 使用 health check 避免服務只依啟動順序、卻在相依服務尚未就緒時連線失敗。
- 使用 named volume 保存資料，使容器能安全重建。

## 注意事項

本專案為課程展示，帳號密碼直接寫在 Compose 中以方便執行。正式環境應改用 `.env`、Docker secrets 或雲端祕密管理服務，並避免將憑證提交至版本控制。
本專案由chatgpt協助書寫完成
