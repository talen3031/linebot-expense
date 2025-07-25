from linebot.models import QuickReply, QuickReplyButton, MessageAction, FlexSendMessage, TextSendMessage

def send_expense_detail(event, line_bot_api, records, cat=None, period_text=None):
    """
    通用支出明細 Flex Message
    - cat: 分類名稱（None 則為全部）
    - period_text: 時間區間（None 則為全部）
    """
    if not records:
        line_bot_api.reply_message(event.reply_token, TextSendMessage("目前沒有紀錄"))
        return

    items = []
    total = 0
    for i, r in enumerate(records):
        amount = int(r.get('amount', 0) or 0)
        desc = r.get('desc', ' ')
        date_str = r['created_at'].strftime("%Y-%m-%d") if r.get("created_at") else " "
        # 是否顯示日期？全部明細不用、分類明細要顯示
        line_contents = [
            {"type": "text", "text": f"{i+1}. {desc}", "size": "sm", "flex": 5 if cat else 4},
            {"type": "text", "text": f"{amount}元", "size": "sm", "flex": 2, "align": "end"},
        ]
        if cat:  # 分類明細要顯示日期
            line_contents.append(
                {"type": "text", "text": date_str, "size": "xs", "color": "#AAAAAA", "flex": 3, "align": "end"}
            )
        else:    # 全部明細要顯示分類
            line_contents.append(
                {"type": "text", "text": f"({r.get('category', '')})", "size": "sm", "color": "#AAAAAA", "flex": 2, "align": "end"}
            )

        items.append({
            "type": "box",
            "layout": "horizontal",
            "contents": line_contents
        })
        total += amount

    # 加總額
    items.append({
        "type": "box",
        "layout": "horizontal",
        "margin": "md",
        "contents": [
            {"type": "text", "text": "總額", "size": "md" if cat else "sm", "weight": "bold", "flex": 5 if cat else 4, "color": "#E0341B" if cat else "#C0504D"},
            {"type": "text", "text": f"{total}元", "size": "md" if cat else "sm", "weight": "bold", "flex": 2, "color": "#E0341B" if cat else "#C0504D", "align": "end"},
            {"type": "text", "text": " ", "flex": 3 if cat else 2}
        ]
    })

    # 標題
    if cat:
        title = f"{period_text or ''}{cat}明細"
        alt_text = title
    else:
        title = "全部明細"
        alt_text = "全部明細"

    flex_data = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": title, "weight": "bold", "size": "lg", "margin": "md"},
                {"type": "separator", "margin": "md"},
                {"type": "box", "layout": "vertical", "margin": "md", "spacing": "sm", "contents": items}
            ]
        }
    }

    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(alt_text=alt_text, contents=flex_data)
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
