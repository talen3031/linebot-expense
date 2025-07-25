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
    # 統計
    if text in day_text_set:
        return {"type": "check", "scope": "day"}
    if text in week_text_set:
        return {"type": "check", "scope": "week"}
    if text in month_text_set:
        return {"type": "check", "scope": "month"}
    
    if text in ("所有統計", "全部統計", "查全部統計"):
        return {"type": "check", "scope": "all_summary"}
    # 查帳
    if text in ("查帳","明細", "所有明細"):
        return {"type": "check", "scope": "all"}
    #
    if text in ("查月份", "月份選單"):
        return {"type": "check", "scope": "month_menu"}
    #查一月統計
    if re.match(r"查(\d{1,2})月統計", text):
        m = re.match(r"查(\d{1,2})月統計", text)
        return {"type": "check", "scope": "month_stat", "month": int(m.group(1))}
    #查一月交通明細
    if re.match(r"查(\d{1,2})月.+", text):
        m = re.match(r"查(\d{1,2})月(.+)", text)
        return {"type": "check", "scope": "month_cat", "month": int(m.group(1)), "cat": m.group(2).strip()}
    #查本月交通
    if re.match(r"查本月.+", text):
        cat = re.match(r"查本月(.+)", text).group(1)
        return {"type": "check", "scope": "this_month_cat", "cat": cat}
    #查本週交通明細
    if re.match(r"查本週.+", text):
        cat = re.match(r"查本週(.+)", text).group(1)
        return {"type": "check", "scope": "this_week_cat", "cat": cat}
    #查本日交通明細
    if re.match(r"查本日.+", text):
        cat = re.match(r"查本日(.+)", text).group(1)
        return {"type": "check", "scope": "today_cat", "cat": cat}
    #查詢所有交通明細
    if re.match(r"查(詢)?所有([^\s]+)", text):
        cat = re.match(r"查(詢)?所有([^\s]+)", text).group(2)
        return {"type": "check", "scope": "all_cat", "cat": cat}

    # 刪除
    if re.match(r"刪除第\s*\d+\s*筆到第\s*\d+\s*筆", text):
        m = re.match(r"刪除第\s*(\d+)\s*筆到第\s*(\d+)\s*筆", text)
        return {"type": "delete", "scope": "range", "start": int(m.group(1))-1, "end": int(m.group(2))-1}
    if re.match(r"刪除第\s*\d+\s*筆", text):
        m = re.match(r"刪除第\s*(\d+)\s*筆", text)
        return {"type": "delete", "scope": "single", "idx": int(m.group(1))-1}
    if text in ("刪除全部", "全部刪除"):
        return {"type": "delete", "scope": "all"}

    # 多行新增紀錄
    if "\n" in text or "\r" in text:
        return {"type": "record", "scope": "multi", "raw": text}

    # 單行
    if re.match(r".+?\s*\d+$", text):
        return {"type": "record", "scope": "single", "raw": text}

    # 預設
    return {"type": "fallback"}
