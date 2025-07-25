# LINE Bot 記帳小幫手

## 專案簡介
本專案是一個運行於 LINE 平台的自動化記帳機器人，讓用戶可以在 LINE 對話中快速輸入支出，機器人會自動分類、儲存、查詢、刪除並彙整統計。

**已成功部署於 Railway 雲端平台：**  
👉 [https://web-production-ef82.up.railway.app/](https://web-production-ef82.up.railway.app/)

首頁提供「一鍵加入好友」按鈕與 QR Code，手機或桌機都能輕鬆加入。  
完成加好友後，即可在 LINE 聊天室輸入「早餐 60」等訊息進行快速記帳。

---

## 主要功能

- **自然語言記帳**：輸入「早餐 60」自動分類與記錄，也支援多筆資料換行輸入。
- **自動分類**：結合 NLP，描述與分類自動對應，支援自訂關鍵字與括號標註（如：機車（交通）100）。
- **查詢/刪除**：查帳、查分類明細、刪除指定筆數/區間/全部支出。
- **統計分析**：本日/本週/本月支出統計，圖表化展現（Flex message 條狀圖），可點擊圖表分類查詢明細。
- **視覺化回覆**：全部回覆皆支援 LINE Flex Message 格式，顯示明細與統計。

---

## 架構說明

- **後端框架**：Flask
- **LINE SDK**：line-bot-sdk
- **資料庫**：MongoDB
- **NLP 分類**：jieba 分詞 + 關鍵字字典自學習

---
## Webhook 架設與 LINE Bot 設定方式

1. **LINE Developers Console 新建 Messaging API channel**
2. **取得 Channel access token、Channel secret**
3. **部署 webhook server（本專案已部署於 Railway）**
4. **在 LINE Developers 設定 Webhook URL 並開啟 Use webhook 開關**  
5. **將 Channel access token、Channel secret、MONGO_URI 等設為環境變數**

## 資料庫 Schema

### expenses（支出紀錄）

| 欄位        | 型別      | 說明                  |
|-------------|-----------|-----------------------|
| _id         | ObjectId  | MongoDB自動產生主鍵   |
| user_id     | string    | LINE User ID          |
| amount      | int/float | 支出金額              |
| desc        | string    | 支出描述              |
| category    | string    | 分類主類（如飲食）    |
| subcategory | string    | 子分類（如早餐）      |
| created_at  | datetime  | 建立時間              |

### categories（分類關鍵字）

| 欄位      | 型別    | 說明                        |
|-----------|---------|-----------------------------|
| _id       | ObjectId| 主鍵                        |
| category  | string  | 分類名稱（如飲食）          |
| keywords  | array   | 關鍵字列表（如["早餐"]）    |
| updated_at| datetime| 更新時間                    |

### users（用戶資訊）

| 欄位         | 型別      | 說明                               |
|--------------|-----------|------------------------------------|
| _id          | ObjectId  | MongoDB自動產生主鍵                |
| line_user_id | string    | LINE User ID（唯一鍵，索引）        |
| display_name | string    | 用戶顯示名稱                       |
| created_at   | datetime  | 加入時間（首次建立記錄時間）        |
| last_active  | datetime  | 最近一次活動時間（可定期更新）      |

## 部署平台與架構

- **平台**：Railway
- **MongoDB 資料庫平台**：MongoDB Atlas
- **Webhook 服務網址**：[https://web-production-ef82.up.railway.app/](https://web-production-ef82.up.railway.app/)

---