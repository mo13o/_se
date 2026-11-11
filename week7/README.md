# 島嶼大學校務行政資訊系統

這是一個以 HTML、CSS、JavaScript 製作的校務系統前端示範專案。專案包含登入頁面、課程查詢、系所篩選、加退選與學分統計。

> 本專案僅為介面與互動展示，不會連接真實學校資料庫，也不應用於儲存真實帳號或個人資料。

## 功能

- 校務系統登入介面
- 動態驗證碼
- 顯示與隱藏密碼
- 課程名稱、課號與教師搜尋
- 開課系所篩選
- 加選與退選
- 已選課程和學分統計
- 額滿課程提示
- 手機與桌面響應式版面

## 示範登入

- 帳號：`S112345678`
- 密碼：`demo1234`
- 驗證碼：依畫面右側顯示的四個字元輸入

目前的前端示範會接受任何非空白帳號與密碼，驗證碼必須正確。

## 專案結構

```text
island-university-portal/
├─ index.html       # 網頁結構
├─ styles.css       # 視覺樣式與響應式版面
├─ app.js           # 登入、搜尋與加退選互動
├─ server.js        # 本機預覽伺服器
├─ package.json     # npm 啟動設定
└─ README.md        # 專案說明
```

## 使用 VS Code 開啟

1. 將 ZIP 解壓縮。
2. 開啟 Visual Studio Code。
3. 選擇「檔案」→「開啟資料夾」。
4. 選擇解壓縮後的 `island-university-portal` 資料夾。

## 啟動方式一：使用 Node.js

電腦需先安裝 Node.js 18 或更新版本。在 VS Code 終端機執行：

```bash
npm start
```

接著用瀏覽器開啟：

```text
http://127.0.0.1:4173
```

本專案不使用任何 npm 第三方套件，因此不需要先執行 `npm install`。

## 啟動方式二：使用 Live Server

1. 在 VS Code 安裝 Live Server 擴充套件。
2. 在檔案總管中對 `index.html` 按右鍵。
3. 選擇「Open with Live Server」。

也可以直接雙擊 `index.html`，但使用本機伺服器會更接近網站正式運作方式。

## 修改課程資料

課程資料位於 `app.js` 開頭的 `courses` 陣列。例如：

```javascript
{
  code: "DMD401",
  name: "互動設計實務",
  teacher: "陳思妤",
  dept: "數位媒體系",
  time: "週四 09:10–12:00",
  credit: 3,
  people: "28 / 35",
  selected: true
}
```

- `full: true`：課程顯示為額滿。
- `selected: true`：預設顯示為已選課程。
- 新增系所時，也需要同步修改 `index.html` 中的系所下拉選單。

## 後續擴充建議

目前所有資料只存在瀏覽器記憶體，重新整理後會回到初始狀態。若要製作正式系統，可再加入：

- 後端 API 與資料庫
- 真實登入及權限驗證
- 密碼雜湊與安全連線
- 課程衝堂及學分上限檢查
- 選課結果永久儲存
- 教師與管理員後台

## 自動化測試

本測試版專案提供三層網站測試：

```text
tests/
├─ unit/server.test.js   # Server 單元測試
├─ system/api.test.js    # 真實 HTTP 與 Web API 系統測試
└─ e2e/portal.spec.js    # Playwright 無頭瀏覽器 E2E 測試
```

第一次執行前安裝套件：

```bash
npm install
```

E2E 測試預設使用電腦已安裝的 Google Chrome，並以 headless 模式執行。若電腦沒有 Chrome，可將 `playwright.config.js` 中的 `channel: "chrome"` 移除，再執行 `npx playwright install chromium`。

執行全部測試：

```bash
npm test
```

也可以分別執行：

```bash
npm run test:unit
npm run test:system
npm run test:e2e
```

### 測試內容

- **單元測試**：Content-Type、靜態路徑安全、課程篩選、帳密驗證。
- **系統測試**：`GET /api/health`、`GET /api/courses`、`POST /api/login` 與首頁 HTTP 回應。
- **E2E 測試**：無頭 Chromium 登入、驗證碼輸入、課程搜尋、加選及學分更新。

## ChatGPT 輔助說明

本專案使用 ChatGPT 輔助完成，協助內容包含系統功能規劃、HTML／CSS／JavaScript 程式撰寫、Node.js Web API 設計，以及單元測試、系統測試和 Playwright E2E 測試的建立與除錯。專案內容經由人工檢查、調整並實際執行測試後完成。

## 授權

此示範專案可作為課堂作業或前端練習使用。若公開發布，請替換學校名稱、標誌與示範資料，避免讓使用者誤認為正式校務網站。
