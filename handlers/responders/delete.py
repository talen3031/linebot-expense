from db import delete_expenses_by_range, delete_expense_by_index, delete_all_expenses
from linebot.models import TextSendMessage

def handle(event, line_bot_api, user_id, command):
    scope = command.get("scope")

    # 刪除範圍（多筆，例如：刪除第3筆到第7筆）
    if scope == "range":
        start_idx, end_idx = command["start"], command["end"]
        if start_idx >= 0 and end_idx >= start_idx:
            deleted_count = delete_expenses_by_range(user_id, start_idx, end_idx)
            if deleted_count:
                msg = f"已刪除第{start_idx+1}筆到第{end_idx+1}筆（共{deleted_count}筆）"
            else:
                msg = "刪除範圍有誤或超出範圍"
        else:
            msg = "請輸入正確的區間"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(msg))

    # 刪除單筆（例如：刪除第2筆）
    elif scope == "single":
        idx = command["idx"]
        if idx >= 0:
            if delete_expense_by_index(user_id, idx):
                msg = f"已刪除第 {idx+1} 筆紀錄"
            else:
                msg = "沒有這一筆"
        else:
            msg = "請輸入正確的筆數"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(msg))

    # 刪除全部
    elif scope == "all":
        count = delete_all_expenses(user_id)
        if count:
            msg = f"已刪除{count}筆紀錄"
        else:
            msg = "沒有紀錄可刪除"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(msg))
