from db import get_all_expenses, summary_by_date_range,get_category_expenses,get_last_expenses
from linemessage import send_flex_summary, send_expense_detail, send_month_menu
from datetime import datetime, timedelta
from linebot.models import TextSendMessage
from collections import defaultdict
def parse_date_safe(val):
    if isinstance(val, datetime):
        return val
    if isinstance(val, str):
        try:
            if len(val) == 10:
                return datetime.strptime(val, "%Y-%m-%d")
            if "T" in val:
                return datetime.fromisoformat(val)
            return datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None
    return None

def handle(event, line_bot_api, user_id, command):
    scope = command.get("scope")
    # 月份選單
    if scope == "month_menu":
        send_month_menu(event, line_bot_api)
    # 查帳（查詢近五筆）
    elif scope == "recent_detail":
        recs = get_last_expenses(user_id)
        send_expense_detail(event, line_bot_api, recs)
     # 查帳（查詢所有明細，純列表）
    elif scope == "all":
        recs = get_all_expenses(user_id)
        send_expense_detail(event, line_bot_api, recs)

    #==================================某分類明細==========================================

    # 指定月份+分類明細（查6月住家、查7月飲食...）
    elif scope == "month_cat":
        month, cat = command["month"], command["cat"]
        today = datetime.now()
        year = today.year
        if today.month < month: year -= 1
        month_start = datetime(year, month, 1)
        month_end = datetime(year+1, 1, 1) if month == 12 else datetime(year, month+1, 1)

        records = []
        for r in get_all_expenses(user_id):
            # 這裡修正型別問題
            created_at = parse_date_safe(r["created_at"])
            if created_at and r["category"] == cat and month_start <= created_at < month_end:
                records.append(r)

        if not records:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(f"{month}月沒有「{cat}」類別的紀錄"))
            return
        send_expense_detail(event, line_bot_api, records, cat, f"{month}月")

    # 本月某分類明細（查本月飲食、查本月交通...）
    elif scope == "this_month_cat":
        cat = command["cat"]
        today = datetime.now()
        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        records = get_category_expenses(user_id, cat, month_start)
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
        records = get_category_expenses(user_id, cat, week_start)
        if not records:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(f"本週沒有「{cat}」類別的紀錄"))
            return
        send_expense_detail(event, line_bot_api, records,cat, "本週")

    # 本日某分類明細（查本日飲食、查本日交通...）
    elif scope == "today_cat":
        cat = command["cat"]
        today = datetime.now()
        day_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        records = get_category_expenses(user_id, cat, day_start)
        
        if not records:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(f"本日沒有「{cat}」類別的紀錄"))
            return
        send_expense_detail(event, line_bot_api, records,cat, "本日")

    # 查詢所有時間的單一分類明細（查所有飲食、查所有交通...）
    elif scope == "all_cat":
        cat = command["cat"]
        records = get_category_expenses(user_id, cat)

        send_expense_detail(event, line_bot_api, records,cat, "全部")

    #==================================統計==========================================

    # 本日統計
    elif scope == "day":
        today = datetime.now()
        day_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        stats = summary_by_date_range(user_id, day_start)
        if not stats:
            line_bot_api.reply_message(event.reply_token, TextSendMessage("本日尚無支出紀錄"))
            return
        send_flex_summary(event, line_bot_api, stats, "本日統計")

    # 本週統計
    elif scope == "week":
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        stats = summary_by_date_range(user_id, week_start)
        if not stats:
            line_bot_api.reply_message(event.reply_token, TextSendMessage("本週尚無支出紀錄"))
            return
        send_flex_summary(event, line_bot_api, stats, "本週統計")

    # 本月統計
    elif scope == "month":
        today = datetime.now()
        month_start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        stats = summary_by_date_range(user_id, month_start)
        if not stats:
            line_bot_api.reply_message(event.reply_token, TextSendMessage("本月尚無支出紀錄"))
            return
        send_flex_summary(event, line_bot_api, stats, "本月統計")
    # 所有分類統計（所有統計、全部統計）
    elif scope == "all_summary":
        stats = summary_by_date_range(user_id)
        if not stats:
            line_bot_api.reply_message(event.reply_token, TextSendMessage("目前沒有任何支出紀錄"))
            return

        send_flex_summary(event, line_bot_api, stats, "所有統計")


    # 指定月份統計（如查7月統計）
    elif scope == "month_stat":
        month = command["month"]
        today = datetime.now()
        year = today.year
        if today.month < month:
            year -= 1

        month_start = datetime(year, month, 1)
        month_end = datetime(year+1, 1, 1) if month == 12 else datetime(year, month+1, 1)

        stats = summary_by_date_range(user_id, month_start, month_end)

        if not stats:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(f"{month}月尚無支出紀錄"))
            return

        send_flex_summary(event, line_bot_api, stats, f"{month}月統計", month)
