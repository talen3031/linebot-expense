from handlers.parser import parse_command
from handlers.responders import check, delete, record, fallback
from db import insert_user, update_user_last_active
from utils.preprocess_text import preprocess_text

def handle_text_message(event, line_bot_api):
    user_id = event.source.user_id
    text = event.message.text.strip()

    # 用戶活躍記錄
    insert_user(user_id)
    update_user_last_active(user_id)

    # 前處理文字（數字、月份中文轉換）
    text = preprocess_text(text)
    command = parse_command(text)

    # 分派
    if command["type"] == "check":
        check.handle(event, line_bot_api, user_id, command)
    elif command["type"] == "delete":
        delete.handle(event, line_bot_api, user_id, command)
    elif command["type"] == "record":
        record.handle(event, line_bot_api, user_id, command)
    else:
        
        fallback.handle(event, line_bot_api)
