from linebot.models import TextSendMessage

def handle(event, line_bot_api):
    hint = (
    "📝 請用「描述 金額」新增支出\n"
    "或輸入：\n"
    "1️⃣ 查帳 或 所有明細\n"
    "2️⃣ 所有統計（查詢全部支出統計）\n"
    "3️⃣ 查月份／月份選單（快速選取不同月份統計）\n"
    "4️⃣ 刪除第1筆／刪除第3筆到第8筆／刪除全部\n"
    "5️⃣ 本月統計／本週統計／本日統計\n"
    "6️⃣ 本月飲食／5月飲食／本週其他／本日交通\n"
    "\n"
    "📋 支援多筆資料換行輸入\n"
    "📈 統計會自動產生圖表！\n"
    "👉 點擊圖表上的分類還可查詢各分類明細"
    )

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(hint)
    )
