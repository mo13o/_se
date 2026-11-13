# BookNest 線上書店管理系統

BookNest 是大學網站開發課程用的全端範例，使用原生 HTML、CSS、JavaScript、Cloudflare Workers 與 Cloudflare D1。專案目前完成 **第一至第四階段**。

## 文件導覽

- [系統架構](docs/ARCHITECTURE.md)
- [資料庫 ER Diagram](docs/ER-DIAGRAM.md)
- [Cloudflare 部署與除錯](docs/DEPLOYMENT.md)
- [教授驗收展示流程](docs/DEMO.md)

## 第一階段完成內容

- Cloudflare Workers 專案與 Wrangler JSONC 設定
- D1 五張主要資料表、限制、外鍵與索引
- 5 種分類、15 本繁體中文測試書籍
- `GET /api/health`
- `GET /api/books?q=關鍵字&category=分類編號&sort=newest|price_asc|price_desc|title`
- `GET /api/books/:id`
- `GET /api/categories`
- 基本 API 自動測試

## 第二階段完成內容

- 響應式首頁、書籍卡片與可收合分類選單
- 書名／作者搜尋、分類篩選及價格／書名排序
- 獨立書籍詳細頁 `book.html?id=書籍編號`
- 載入中、無結果及 API 錯誤狀態
- 所有書籍內容皆由 Worker API 與 D1 提供

## 第三階段完成內容

- localStorage 購物車、商品數量修改與移除
- 購物車數量徽章與即時計算總金額
- 訂購人姓名、Email 與訂單確認介面
- `POST /api/orders` 建立 D1 訂單及訂單明細
- 後端重新查價、檢查庫存並原子扣減庫存
- `client_order_id` 防止連點或重試造成重複訂單
- 訂單完成視窗顯示訂單編號、金額與狀態

## 第四階段完成內容

- PBKDF2-SHA256 管理員密碼雜湊
- HttpOnly、SameSite Session Cookie 與 D1 Session 資料表
- 所有 `/api/admin/*` 管理 API 後端權限檢查
- 書籍新增、修改、庫存調整及下架
- 訂單紀錄列表
- 響應式管理後台

本機展示帳號：`admin`／`BookNest123!`。正式部署前請更換預設密碼雜湊。

## 專案結構

```text
booknest/
├─ migrations/
│  ├─ 0001_initial_schema.sql   # 資料表、限制、外鍵、索引
│  └─ 0002_seed_data.sql        # 5 分類與 15 本測試書
├─ public/
│  ├─ index.html                # 首頁與書籍列表
│  ├─ book.html                 # 書籍詳細頁
│  ├─ app.js                    # 首頁 API 呼叫與互動
│  ├─ book.js                   # 單本書籍 API 呼叫
│  ├─ cart.html                 # 購物車與結帳頁
│  ├─ cart.js                   # 購物車操作與建立訂單
│  ├─ cart-store.js             # localStorage 購物車共用工具
│  └─ styles.css                # 全站響應式樣式
├─ src/
│  ├─ routes/
│  │  ├─ books.js               # 書籍查詢 API
│  │  └─ categories.js          # 分類查詢 API
│  ├─ http.js                   # 統一 JSON 回應工具
│  └─ index.js                  # Worker 入口與路由
├─ test/
│  └─ routes.test.js            # Node 內建測試
├─ package.json
└─ wrangler.jsonc
```

## 環境需求

- Node.js 20 以上（建議使用目前 LTS）
- npm
- 第五階段遠端部署時才需要 Cloudflare 帳號與 `wrangler login`

## 本機執行

```bash
npm install
npm run db:migrate:local
npm run db:check:local
npm run dev
```

開啟 `http://localhost:8787`，並測試：

```text
http://localhost:8787/api/health
http://localhost:8787/api/books
http://localhost:8787/api/books?q=SQL
http://localhost:8787/api/books?category=2&sort=price_asc
http://localhost:8787/api/books/1
http://localhost:8787/api/categories
```

執行自動測試：

```bash
npm test
```

## D1 設計重點

- `price`、`total_amount` 使用新台幣整數，避免浮點數誤差。
- `order_items.unit_price` 保存下單當時單價。
- `books.is_active` 支援下架，不直接刪除已被訂單引用的書籍。
- 外鍵避免孤兒資料，`CHECK` 避免負價格、負庫存與無效數量。
- `admins.password_hash` 只允許保存安全雜湊；預設管理員於第四階段建立，不提交明文密碼。

## 正式 D1（第五階段執行）

```bash
npx wrangler login
npx wrangler d1 create booknest-db --location apac
```

將指令回傳的 `database_id` 寫入 `wrangler.jsonc`，再執行：

```bash
npm run db:migrate:remote
npx wrangler deploy
```

目前使用全零 UUID 供本機測試；正式部署前必須替換，避免綁定到錯誤資料庫。
