import re
from nlp import nlp_classify
from db import insert_expense
from datetime import datetime
from linebot.models import TextSendMessage

def handle(event, line_bot_api, user_id, command):
    scope = command.get("scope")
    #多筆新增
    if scope == "multi":
        lines = command["raw"].splitlines()
        added_msgs = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            match = re.match(r"(.+?)\s*(\d+)$", line)
            if match:
                desc, amount = match.groups()
                amount = int(amount)
                category, desc = nlp_classify(desc)
                insert_expense(user_id, category, amount, desc, datetime.now())
                added_msgs.append(f"{desc}（{category}） {amount}元")
            else:
                added_msgs.append(f"❌ 無法辨識：「{line}」")
        reply = "已記錄：\n" + "\n".join(added_msgs)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(reply))
    #單筆新增
    
    elif scope == "single":
        match = re.match(r"(.+?)\s*(\d+)$", command["raw"])
        if match:
            desc, amount = match.groups()
            amount = int(amount)
            category, desc = nlp_classify(desc)
            insert_expense(user_id, category, amount, desc, datetime.now())
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    f"📝 已記錄\n"
                    f"🗒️ 描述：{desc}\n"
                    f"📂 類別：{category}\n"
                    f"💰 金額：{amount} 元"
                )
            )
