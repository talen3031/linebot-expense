from db import get_all_expenses, _summary
from linemessage import send_flex_summary, send_expense_detail, send_month_menu
from datetime import datetime, timedelta
from linebot.models import TextSendMessage

def handle(event, line_bot_api, user_id, command):
    scope = command.get("scope")

    # 查帳（查詢所有明細，純列表）
    if scope == "all":
        recs = get_all_expenses(user_id)
        send_expense_detail(event, line_bot_api, recs)

    # 月份選單
    elif scope == "month_menu":
        send_month_menu(event, line_bot_api)

    # 所有分類統計（所有統計、全部統計）
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
        send_flex_summary(event, line_bot_api, stats, "所有統計")

    # 指定月份統計（如查7月統計）
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
        send_flex_summary(event, line_bot_api, stats, f"{month}月統計", month)

    # 指定月份+分類明細（查7月飲食、查7月交通...）
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
        send_expense_detail(event, line_bot_api, records,cat, f"{month}月")

    # 本月某分類明細（查本月飲食、查本月交通...）
    elif scope == "this_month_cat":
        cat = command["cat"]
        today = datetime.now()
        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        records = [r for r in get_all_expenses(user_id) if r['category'] == cat and r['created_at'] >= month_start]
        if not records:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(f"本月沒有「{cat}」類別的紀錄"))
            return
        send_expense_detail(event, line_bot_api, records,cat, "本月")

    # 本週某分類明細（查本週飲食、查本週交通...）
    elif scope == "this_week_cat":
        cat = command["cat"]
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        records = [r for r in get_all_expenses(user_id) if r['category'] == cat and r['created_at'] >= week_start]
        if not records:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(f"本週沒有「{cat}」類別的紀錄"))
            return
        send_expense_detail(event, line_bot_api, records,cat, "本週")

    # 本日某分類明細（查本日飲食、查本日交通...）
    elif scope == "today_cat":
        cat = command["cat"]
        today = datetime.now()
        day_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        records = [r for r in get_all_expenses(user_id) if r['category'] == cat and r['created_at'] >= day_start]
        if not records:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(f"本日沒有「{cat}」類別的紀錄"))
            return
        send_expense_detail(event, line_bot_api, records,cat, "本日")

    # 查詢所有時間的單一分類明細（查所有飲食、查所有交通...）
    elif scope == "all_cat":
        cat = command["cat"]
        records = [r for r in get_all_expenses(user_id) if r['category'] == cat]
        send_expense_detail(event, line_bot_api, records,cat, "全部")

    # 本日統計
    elif scope == "day":
        today = datetime.now()
        day_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        stats = _summary(user_id, day_start)
        send_flex_summary(event, line_bot_api, stats, "本日統計")

    # 本週統計
    elif scope == "week":
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        stats = _summary(user_id, week_start)
        send_flex_summary(event, line_bot_api, stats, "本週統計")

    # 本月統計
    elif scope == "month":
        today = datetime.now()
        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        stats = _summary(user_id, month_start)
        send_flex_summary(event, line_bot_api, stats, "本月統計")
