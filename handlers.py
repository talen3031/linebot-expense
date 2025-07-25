import re,os
from datetime import datetime, timedelta
from linebot.models import TextSendMessage, FlexSendMessage, ImageSendMessage

from nlp import nlp_classify
from db import insert_expense, delete_expenses_by_range
from db import delete_expense_by_index, _summary,get_all_expenses,delete_all_expenses
from db import insert_user, update_user_last_active

# from upload import upload_to_cloudinary
# from utils.plot import generate_weekly_chart
from utils.chinese_to_digit import chinese_to_digit
from linemessage import send_flex_summary,send_category_detail,send_all_detail

day_text_set={"本日總結", "本日總額", "今日總額", "總額", "總結","今天花多少","今日花多少","花多少"}

week_text_set={"本周總結","本週總額",  "本周總額","本周總結","本週總結",
  "這週總額", "這周總額", "這週總結", "這周總結","這周花多少","這週花多少."}

month_text_set={"本月總結", "本月總額", "這個月總額", "這個月花多少", "這個月總結"}



def handle_text_message(event, line_bot_api):
    user_id = event.source.user_id
    text = event.message.text.strip()
    insert_user(user_id)
    update_user_last_active(user_id)
    # === 1. 查帳（純文字版）===
    if text == "查帳":
        recs = get_all_expenses(user_id)
        send_all_detail(event, line_bot_api, recs)
        return
    

    # 查本月分類明細
    m = re.match(r"查本月(.+)", text)
    if m:
        cat = m.group(1)
        today = datetime.now()
        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        records = [
            r for r in get_all_expenses(user_id)
            if r['category'] == cat and r['created_at'] >= month_start
        ]
        if not records:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(f"本月沒有「{cat}」類別的紀錄")
            )
            return
        send_category_detail(event, line_bot_api, cat, records, "本月")
        return

    # 查本週分類明細
    m = re.match(r"查本週(.+)", text)
    if m:
        cat = m.group(1)
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        records = [
            r for r in get_all_expenses(user_id)
            if r['category'] == cat and r['created_at'] >= week_start
        ]
        if not records:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(f"本週沒有「{cat}」類別的紀錄")
            )
            return
        send_category_detail(event, line_bot_api, cat, records, "本週")
        return

    # 查本日分類明細
    m = re.match(r"查本日(.+)", text)
    if m:
        cat = m.group(1)
        today = datetime.now()
        day_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        records = [
            r for r in get_all_expenses(user_id)
            if r['category'] == cat and r['created_at'] >= day_start
        ]
        if not records:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(f"本日沒有「{cat}」類別的紀錄")
            )
            return
        send_category_detail(event, line_bot_api, cat, records, "本日")
        return


    m = re.match(r"查(詢)?所有([^\s]+)", text)
    if m:
        cat_name = m.group(2)
        records = [r for r in get_all_expenses(user_id) if r['category'] == cat_name]
        send_category_detail(event, line_bot_api, cat_name, records,"全部")
        return
    

    # === 刪除第X筆到第Y筆 ===
    m = re.match(r"刪除第\s*([0-9一二三四五六七八九十]+)\s*筆到第\s*([0-9一二三四五六七八九十]+)\s*筆", text)
    if m:
        print("debug 刪除第X筆到第Y筆 :",m)
        start_idx_str = m.group(1)
        end_idx_str = m.group(2)
        # 轉成數字
        try:
            start_idx = int(start_idx_str) - 1
        except ValueError:
            start_idx = chinese_to_digit(start_idx_str) - 1
        try:
            end_idx = int(end_idx_str) - 1
        except ValueError:
            end_idx = chinese_to_digit(end_idx_str) - 1

        if start_idx >= 0 and end_idx >= start_idx:
            deleted_count = delete_expenses_by_range(user_id, start_idx, end_idx)
            if deleted_count:
                msg = f"已刪除第{start_idx+1}筆到第{end_idx+1}筆（共{deleted_count}筆）"
            else:
                msg = "刪除範圍有誤或超出範圍"
        else:
            msg = "請輸入正確的區間"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(msg))
        return
    # === 刪除第X筆 ===
    m = re.match(r"刪除第\s*([0-9一二兩三四五六七八九十]+)\s*筆", text)
    if m:
        print("debug 刪除第X筆 :",m)
        idx_str = m.group(1)
        # 先轉成數字
        try:
            idx = int(idx_str) - 1
        except ValueError:
            idx = chinese_to_digit(idx_str) - 1
        if idx >= 0:
            if delete_expense_by_index(user_id, idx):
                msg = f"已刪除第 {idx+1} 筆紀錄"
            else:
                msg = "沒有這一筆"
        else:
            msg = "請輸入正確的筆數"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(msg))
        return
    
    # === 刪除全部紀錄 ===
    if text == "刪除全部" or text == "全部刪除":
        count = delete_all_expenses(user_id)
        if count:
            msg = f"已刪除{count}筆紀錄"
        else:
            msg = "沒有紀錄可刪除"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(msg))
        return
    
    # 本日總結
    if text in day_text_set:
        today = datetime.now()
        day_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        stats = _summary(user_id, day_start)
        send_flex_summary(event, line_bot_api, stats, "本日")
        return

    # 本週總結
    if text in week_text_set:
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        stats = _summary(user_id, week_start)
        send_flex_summary(event, line_bot_api, stats, "本週")
        return

    # 本月總結
    if text in month_text_set:
        today = datetime.now()
        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        stats = _summary(user_id, month_start)
        send_flex_summary(event, line_bot_api, stats, "本月")
        return

    # === 4. 多行批次記帳 ===
    lines = text.splitlines()
    if len(lines) > 1:
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
        return


    # === 5. 單行記帳 ===
    match = re.match(r"(.+?)\s*(\d+)$", text)
    if match:
        desc, amount = match.groups()
        amount = int(amount)
        category, desc = nlp_classify(desc)   
        insert_expense(user_id, category, amount, desc, datetime.now())
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(f"已記錄：{desc}（{category}） {amount}元")
        )
        return
    
    hint = (
    "📝 請用「描述 金額」新增支出\n"
    "或輸入：\n"
    "1️⃣ 查帳\n"
    "2️⃣ 刪除第1筆\n"
    "3️⃣ 刪除全部\n"
    "4️⃣ 刪除第3筆到第8筆\n"
    "5️⃣ 本月總結／本週總結／本日總結\n"
    "\n"
    "📋 也支援多筆資料換行輸入\n"
    "📈 統計會自動產生圖表！"
    )
    # === 6. 預設回應 ===
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(hint)
    )
    