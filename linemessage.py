from linebot.models import QuickReply, QuickReplyButton, MessageAction, FlexSendMessage, TextSendMessage

def send_all_detail(event, line_bot_api, records):
    if not records:
        line_bot_api.reply_message(event.reply_token, TextSendMessage("目前沒有紀錄"))
        return

    items = []
    total_amount = 0
    for i, r in enumerate(records):
        amount = int(r.get('amount', 0) or 0)
        items.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {"type": "text", "text": f"{i+1}. {r.get('desc', ' ')}", "size": "sm", "flex": 4},
                {"type": "text", "text": f"{amount}元", "size": "sm", "flex": 2, "align": "end"},
                {"type": "text", "text": f"({r.get('category', '')})", "size": "sm", "color": "#AAAAAA", "flex": 2, "align": "end"}
            ]
        })
        total_amount += amount

    # 新增總額
    items.append({
        "type": "box",
        "layout": "horizontal",
        "contents": [
            {"type": "text", "text": "總額", "size": "sm", "weight": "bold", "flex": 4, "color": "#C0504D"},
            {"type": "text", "text": f"{total_amount}元", "size": "sm", "weight": "bold", "flex": 2, "color": "#C0504D", "align": "end"},
            {"type": "text", "text": " ", "size": "sm", "flex": 2}
        ]
    })

    flex_data = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "全部紀錄", "weight": "bold", "size": "lg", "margin": "md"},
                {"type": "separator", "margin": "md"},
                {"type": "box", "layout": "vertical", "margin": "md", "spacing": "sm", "contents": items}
            ]
        }
    }
    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(alt_text="全部紀錄", contents=flex_data)
    )

def send_category_detail(event, line_bot_api, cat, records, period_text):
    # 統計總額
    total = 0
    items = []
    for i, r in enumerate(records):
        amount = int(r.get('amount', 0) or 0)
        date_str = r['created_at'].strftime("%Y-%m-%d") if r.get("created_at") else " "
        items.append({
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {"type": "text", "text": f"{i+1}. {r.get('desc', ' ')}", "size": "sm", "flex": 5},
                {"type": "text", "text": f"{amount}元", "size": "sm", "flex": 2, "align": "end"},
                {"type": "text", "text": date_str, "size": "xs", "color": "#AAAAAA", "flex": 3, "align": "end"}
            ]
        })
        total += amount

    # 加總額
    items.append({
        "type": "box",
        "layout": "horizontal",
        "margin": "md",
        "contents": [
            {"type": "text", "text": f"總額", "size": "md", "weight": "bold", "flex": 5, "color": "#E0341B"},
            {"type": "text", "text": f"{total}元", "size": "md", "weight": "bold", "flex": 2, "color": "#E0341B", "align": "end"},
            {"type": "text", "text": " ", "flex": 3}
        ]
    })

    flex_data = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": f"{period_text}{cat}明細", "weight": "bold", "size": "lg", "margin": "md"},
                {"type": "separator", "margin": "md"},
                {"type": "box", "layout": "vertical", "margin": "md", "spacing": "sm", "contents": items}
            ]
        }
    }

    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(alt_text=f"{period_text}{cat}明細", contents=flex_data)
    )

from linebot.models import (
    QuickReply, QuickReplyButton, MessageAction, FlexSendMessage, TextSendMessage
)

def send_flex_summary(event, line_bot_api, stats, period_text="本期", month_number=None):
    if not stats:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                f"{period_text}尚無紀錄",
                quick_reply=QuickReply(items=[
                    QuickReplyButton(action=MessageAction(label="本日統計", text="本日統計")),
                    QuickReplyButton(action=MessageAction(label="本週統計", text="本週統計")),
                    QuickReplyButton(action=MessageAction(label="本月統計", text="本月統計")),
                    QuickReplyButton(action=MessageAction(label="查看明細", text="查帳"))
                ])
            )
        )
        return

    total_amount = sum(r['total'] for r in stats)
    if total_amount == 0:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                f"{period_text}沒有支出紀錄",
                quick_reply=QuickReply(items=[
                    QuickReplyButton(action=MessageAction(label="本日統計", text="本日統計")),
                    QuickReplyButton(action=MessageAction(label="本週統計", text="本週統計")),
                    QuickReplyButton(action=MessageAction(label="本月統計", text="本月統計")),
                    QuickReplyButton(action=MessageAction(label="查看明細", text="查帳"))
                ])
            )
        )
        return

    category_colors = {
        "學習": "#4F98FF",
        "住家": "#AD7CFF",
        "飲食": "#42C686",
        "稅金": "#FFB648",
        "娛樂購物": "#FF5E57",
        "醫療": "#FF82A9",
        "交通": "#0099C6",
        "金融": "#B1C1C1",
        "其他": "#B0B0B0"
    }

    category_icons = {
        "學習": "📘",
        "住家": "🏠",
        "飲食": "🍚",
        "稅金": "💸",
        "娛樂購物": "🎮",
        "醫療": "🏥",
        "交通": "🚇",
        "金融": "💰",
        "其他": "🔖"
    }

    if month_number is not None:
        cmd_prefix = f"查{month_number}月"
    elif period_text == "所有紀錄":
        cmd_prefix = "查所有"
    else:
        period_cmd_map = {
            "本月": "查本月",
            "本週": "查本週",
            "本日": "查本日",
            "本期": "查本期"
        }
        cmd_prefix = period_cmd_map.get(period_text, "查")

    stats = sorted(stats, key=lambda r: -r['total'])
    BAR_MAX = 20

    items = []
    for r in stats:
        category = r['_id']
        amount = r['total']
        bar_flex = max(int((amount / total_amount) * BAR_MAX), 1)
        remainder_flex = BAR_MAX - bar_flex
        percent = int(amount / total_amount * 100)
        color = category_colors.get(category, "#B0B0B0")
        icon = category_icons.get(category, "🔖")

        items.append({
            "type": "box",
            "layout": "vertical",
            "margin": "md",
            "action": {
                "type": "message",
                "text": f"{cmd_prefix}{category}"
            },
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": f"{icon} {category}", "size": "sm", "flex": 4, "weight": "bold"},
                        {"type": "text", "text": f"{amount}元", "size": "sm", "flex": 2, "align": "end"}
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "height": "16px",
                    "margin": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": bar_flex,
                            "backgroundColor": color,
                            "cornerRadius": "8px",
                            "contents": [{"type": "filler"}]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "flex": remainder_flex,
                            "backgroundColor": "#F0F0F0",
                            "cornerRadius": "8px",
                            "contents": [{"type": "filler"}]
                        }
                    ]
                },
                {
                    "type": "text",
                    "text": f"{percent}%",
                    "size": "xs",
                    "color": "#AAAAAA",
                    "margin": "sm",
                    "align": "end"
                }
            ]
        })

    items.append({
        "type": "box",
        "layout": "horizontal",
        "margin": "md",
        "contents": [
            {"type": "text", "text": f"{period_text}總額", "size": "md", "weight": "bold", "flex": 4, "color": "#E0341B"},
            {"type": "text", "text": f"{total_amount}元", "size": "md", "weight": "bold", "flex": 2, "color": "#E0341B", "align": "end"}
        ]
    })

    flex_data = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": f"{period_text}支出統計", "weight": "bold", "size": "xl", "margin": "md"},
                {"type": "separator", "margin": "md"},
                {"type": "box", "layout": "vertical", "margin": "md", "spacing": "md", "contents": items}
            ]
        }
    }

    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(
            alt_text=f"{period_text}支出統計",
            contents=flex_data,
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="本日統計", text="本日統計")),
                QuickReplyButton(action=MessageAction(label="本週統計", text="本週統計")),
                QuickReplyButton(action=MessageAction(label="本月統計", text="本月統計")),
                QuickReplyButton(action=MessageAction(label="查所有明細", text="查帳"))
            ])
        )
    )


def send_month_menu(event, line_bot_api):
    buttons = []
    for i in range(1, 13):
        buttons.append({
            "type": "button",
            "style": "primary",
            "color": "#42C686",
            "action": {
                "type": "message",
                "label": f"{i}月",
                "text": f"查{i}月統計"
            }
        })

    # 將 12 個按鈕切成 4 行，每行 3 個
    rows = []
    for i in range(0, 12, 3):
        rows.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "contents": buttons[i:i+3]
        })


    flex_data = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "📅 請選擇月份",
                    "weight": "bold",
                    "size": "xl"
                },
                {
                    "type": "separator"
                },
                *rows
            ]
        }
    }

    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(
            alt_text="月份查詢選單",
            contents=flex_data
        )
    )
