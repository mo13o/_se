# 習題 1：MiniCurl

題目來源：https://github.com/ccc115a/_se/issues/1

本專案以 Python 標準函式庫實作簡易 curl 類型的 HTTP 命令列工具，可傳送請求、查看回應標頭，以及下載檔案。題目頁面沒有額外的功能規格，因此以常見 HTTP 操作作為實作範圍。

## 執行環境

- Python 3.10 以上，不需安裝第三方套件。
- 在終端機切換至本資料夾後執行以下指令。
- Windows 若使用 `py` 啟動 Python，可將指令中的 `python` 改成 `py`。

## 使用方式

```powershell
# 顯示說明
python minicurl.py --help

# GET：取得網頁
python minicurl.py https://example.com

# 顯示回應標頭與本文
python minicurl.py -i https://example.com

# HEAD：只取得標頭
python minicurl.py -I https://example.com

# 跟隨重新導向並下載檔案
python minicurl.py -L -o page.html https://example.com

# POST：傳送表單資料（範例測試服務）
python minicurl.py -d 'name=student&course=se' https://httpbin.org/post

# 指定方法、標頭與本文
python minicurl.py -X PUT -H 'Content-Type: text/plain; charset=utf-8' -d 'Hello' https://httpbin.org/put

# HTTP 錯誤回傳非零結束碼
python minicurl.py -f --timeout 5 https://example.com
```

網路範例需要可用的網路與服務；自動測試使用本機伺服器，不依賴上述外部網站。

## 支援參數

| 參數 | 功能 |
| --- | --- |
| URL | 必填，只接受 HTTP 或 HTTPS |
| `-X`, `--request` | 指定 HTTP 方法 |
| `-H`, `--header` | 自訂標頭，可多次使用 |
| `-d`, `--data` | UTF-8 請求本文；未指定方法時使用 POST |
| `-I`, `--head` | 傳送 HEAD 並印出標頭 |
| `-i`, `--include` | 輸出包含回應標頭 |
| `-L`, `--location` | 跟隨重新導向；預設不跟隨 |
| `-o`, `--output` | 寫入檔案；同名檔案會被覆寫 |
| `--timeout` | socket 等待逾時秒數，預設 10 秒，並非整次下載的總時間限制 |
| `-f`, `--fail` | HTTP 4xx/5xx 時結束碼為 22，且不輸出本文 |

`-I` 不可搭配 `-d` 或 `-X`。使用 `-d` 而未設定 Content-Type 時，標準函式庫使用 application/x-www-form-urlencoded；程式不會自動對資料進行表單編碼。若傳 JSON，需自行提供正確 JSON 字串和 Content-Type。

## 程式設計說明

1. 以 `argparse` 解析命令列參數並檢查輸入。
2. 以 `urllib.request.Request` 建立 URL、方法、標頭與本文。
3. 以 `urllib.request` 傳送請求，HTTPS 使用預設憑證驗證。
4. 將 HTTP 錯誤回應與連線失敗分開處理；未使用 `-f` 時仍可讀取 404 等回應本文。
5. 每次讀取最多 64 KiB，直接輸出原始位元組，避免破壞圖片等二進位檔案。
6. 重新導向採 Python 標準函式庫語意；跨來源時移除 Authorization、Cookie 與 Proxy-Authorization 標頭。

結束碼：0 為完成 HTTP 處理；1 為連線、檔案或其他輸入錯誤；2 為命令列參數錯誤；22 為使用 `-f` 時收到 HTTP 4xx/5xx。

## 測試

```powershell
python -m unittest discover -s . -v
```

已通過 9 項本機整合測試：GET、POST 與自訂標頭、PUT 與中文本文、HEAD、包含回應標頭、重新導向、二進位下載、HTTP 錯誤，以及非法輸入。

測試會啟動臨時本機 HTTP 伺服器，以子程序執行 CLI，檢查實際輸出、檔案內容和結束碼；結束後關閉伺服器。未進行外部 HTTPS 連線測試。

## 限制與可擴充功能

這是教學用途的精簡實作，不與完整 curl 逐項相容。目前不支援 FTP、HTTP/2、multipart 檔案上傳、`-d @file`、cookie jar、斷點續傳及自動解壓縮。重新導向的方法轉換依 Python 行為，與 curl 的部分選項語意可能不同。下載失敗時可能留下部分檔案；可擴充為暫存檔完成後再替換。

## 檔案

- `minicurl.py`：主程式。
- `test_minicurl.py`：本機整合測試。
- `submission-draft.md`：尚未發佈的繳交留言草稿。

本專案由 AI 協助實作與測試。
