import re

day_text_set = {
    "本日統計", "今日統計", "今天統計",
    "本日總額", "今日總額", "今天總額",
    "總額", "統計", "今天花多少", "今日花多少", "本日花多少", "花多少"
}

week_text_set = {
    "本週統計", "本周統計",
    "本週總額", "本周總額",
    "這週統計", "這周統計",
    "這週總額", "這周總額",
    "這週花多少", "這周花多少", "本週花多少", "本周花多少"
}

month_text_set = {
    "本月統計", "這個月統計", "本月份統計",
    "本月總額", "這個月總額", "本月份總額",
    "這個月花多少", "本月花多少", "本月份花多少"
}
def parse_command(text):
    print("text:",text)
    # 統計：本日
    if text in day_text_set:
        return {"type": "check", "scope": "day"}
    # 統計：本週
    if text in week_text_set:
        return {"type": "check", "scope": "week"}
    # 統計：本月
    if text in month_text_set:
        return {"type": "check", "scope": "month"}

    # 統計：全部支出
    if text in ("所有統計", "全部統計", "查全部統計"):
        return {"type": "check", "scope": "all_summary"}
    
    # 查帳（最近五筆明細）
    if text == "查帳":
        return {"type": "check", "scope": "recent_detail"}

    # 查詢所有明細（全部歷史資料）
    if text in ("明細", "所有明細"):
        return {"type": "check", "scope": "all"}
    
    # 月份選單
    if text in ("查月份", "月份選單"):
        return {"type": "check", "scope": "month_menu"}

    # 查詢 x 月統計
    m = re.match(r"(\d{1,2})月統計", text)
    if m:
        return {"type": "check", "scope": "month_stat", "month": int(m.group(1))}

    # 查詢 x 月某分類（如 7月飲食）
    m = re.match(r"(\d{1,2})月(.+)", text)
    if m:
        return {"type": "check", "scope": "month_cat", "month": int(m.group(1)), "cat": m.group(2).strip()}

    # 查詢本月某分類（如本月飲食）
    m = re.match(r"本月(.+)", text)
    if m:
        return {"type": "check", "scope": "this_month_cat", "cat": m.group(1).strip()}

    # 查詢本週某分類（如本週娛樂）
    m = re.match(r"本週(.+)", text)
    if m:
        return {"type": "check", "scope": "this_week_cat", "cat": m.group(1).strip()}

    # 查詢本日某分類（如本日交通）
    m = re.match(r"本日(.+)", text)
    if m:
        return {"type": "check", "scope": "today_cat", "cat": m.group(1).strip()}

    # 查詢所有某分類（如所有飲食）
    m = re.match(r"所有([^\s]+)", text)
    if m:
        return {"type": "check", "scope": "all_cat", "cat": m.group(1).strip()}

    # 刪除第x筆到第y筆
    m = re.match(r"刪除第\s*(\d+)\s*筆到第\s*(\d+)\s*筆", text)
    if m:
        print("刪除第x筆到第y筆")
        return {"type": "delete", "scope": "range", "start": int(m.group(1)) - 1, "end": int(m.group(2)) - 1}
    
    # 刪除單一筆（如刪除第2筆）
    m = re.match(r"刪除第\s*(\d+)\s*筆", text)
    if m:
        print("刪除第x筆")
        return {"type": "delete", "scope": "single", "idx": int(m.group(1)) - 1}
    
    # 刪除全部
    if text in ("刪除全部", "全部刪除"):
        return {"type": "delete", "scope": "all"}

    # 多行新增（有換行的記錄）
    if "\n" in text or "\r" in text:
        return {"type": "record", "scope": "multi", "raw": text}

    # 單行新增（格式如「早餐 60」）
    if re.match(r".+?\s*\d+$", text):
        return {"type": "record", "scope": "single", "raw": text}

    # 預設fallback，無法解析時
    return {"type": "fallback"}
