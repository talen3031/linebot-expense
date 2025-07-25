from db import get_all_expenses, _summary
from linemessage import send_flex_summary, send_category_detail, send_all_detail, send_month_menu
from datetime import datetime, timedelta
from linebot.models import TextSendMessage

def handle(event, line_bot_api, user_id, command):
    scope = command.get("scope")

    if scope == "all":
        recs = get_all_expenses(user_id)
        send_all_detail(event, line_bot_api, recs)
    elif scope == "month_menu":
        send_month_menu(event, line_bot_api)
    elif scope == "all_summary":
        records = get_all_expenses(user_id)
        if not records:
            line_bot_api.reply_message(event.reply_token, TextSendMessage("目前沒有任何支出紀錄"))
            return
        from collections import defaultdict
        summary = defaultdict(int)
        for r in records:
            summary[r["category"]] += r["amount"]
        stats = [{"_id": k, "total": v} for k, v in summary.items()]
        send_flex_summary(event, line_bot_api, stats, "所有紀錄")
        
    elif scope == "month_stat":
        month = command["month"]
        today = datetime.now()
        year = today.year
        if today.month < month: year -= 1
        month_start = datetime(year, month, 1)
        month_end = datetime(year+1, 1, 1) if month == 12 else datetime(year, month+1, 1)
        records = [r for r in get_all_expenses(user_id) if month_start <= r["created_at"] < month_end]
        if not records:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(f"{month}月尚無支出紀錄"))
            return
        from collections import defaultdict
        summary = defaultdict(int)
        for r in records:
            summary[r["category"]] += r["amount"]
        stats = [{"_id": k, "total": v} for k, v in summary.items()]
        send_flex_summary(event, line_bot_api, stats, f"{month}月", month)
    elif scope == "month_cat":
        month, cat = command["month"], command["cat"]
        today = datetime.now()
        year = today.year
        if today.month < month: year -= 1
        month_start = datetime(year, month, 1)
        month_end = datetime(year+1, 1, 1) if month == 12 else datetime(year, month+1, 1)
        records = [r for r in get_all_expenses(user_id) if r["category"] == cat and month_start <= r["created_at"] < month_end]
        if not records:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(f"{month}月沒有「{cat}」類別的紀錄"))
            return
        send_category_detail(event, line_bot_api, cat, records, f"{month}月")
    elif scope == "this_month_cat":
        cat = command["cat"]
        today = datetime.now()
        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        records = [r for r in get_all_expenses(user_id) if r['category'] == cat and r['created_at'] >= month_start]
        if not records:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(f"本月沒有「{cat}」類別的紀錄"))
            return
        send_category_detail(event, line_bot_api, cat, records, "本月")
    elif scope == "this_week_cat":
        cat = command["cat"]
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        records = [r for r in get_all_expenses(user_id) if r['category'] == cat and r['created_at'] >= week_start]
        if not records:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(f"本週沒有「{cat}」類別的紀錄"))
            return
        send_category_detail(event, line_bot_api, cat, records, "本週")
    elif scope == "today_cat":
        cat = command["cat"]
        today = datetime.now()
        day_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        records = [r for r in get_all_expenses(user_id) if r['category'] == cat and r['created_at'] >= day_start]
        if not records:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(f"本日沒有「{cat}」類別的紀錄"))
            return
        send_category_detail(event, line_bot_api, cat, records, "本日")
    elif scope == "all_cat":
        cat = command["cat"]
        records = [r for r in get_all_expenses(user_id) if r['category'] == cat]
        send_category_detail(event, line_bot_api, cat, records, "全部")
    elif scope == "day":
        today = datetime.now()
        day_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        stats = _summary(user_id, day_start)
        send_flex_summary(event, line_bot_api, stats, "本日")
    elif scope == "week":
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        stats = _summary(user_id, week_start)
        send_flex_summary(event, line_bot_api, stats, "本週")
    elif scope == "month":
        today = datetime.now()
        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        stats = _summary(user_id, month_start)
        send_flex_summary(event, line_bot_api, stats, "本月")
