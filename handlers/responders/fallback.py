from linebot.models import TextSendMessage

def handle(event, line_bot_api):
    hint = (
    "📝 請用「描述 金額」新增支出\n"
    "📋 支援多筆資料換行輸入\n"
    "\n"
    "📌 可以輸入以下指令查詢支出紀錄：\n"
    "✔️【前兩字】：所有、本月、本週、本日、6月、7月...（代表時間範圍）\n"
    "✔️【後兩字】：統計 或 類別名稱（如：飲食、交通、醫療...）\n"
    "\n"
    "📊 範例：\n"
    "• 本月統計（查看本月所有分類的總花費）\n"
    "• 6月醫療（查詢 6 月份的醫療支出）\n"
    "\n"
    "📋 其他功能：\n"
    "• 查帳 / 所有明細（查看最近支出）\n"
    "• 查月份/月份選單（快速選擇月份統計）\n"
    "• 刪除第1筆 / 刪除第3筆到第8筆 / 刪除全部\n"
    "\n"
    "📈 統計會自動產生圖表！\n"
    "👉 點擊圖表分類還能查看明細"
)


    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(hint)
    )
