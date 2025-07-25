from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from handlers import handle_text_message

app = Flask(__name__)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
@app.route("/callback", methods=['POST'])
def callback():
    print("==收到 LINE webhook ==")
    try:
        signature = request.headers.get('X-Line-Signature', 'no-signature')
        body = request.get_data(as_text=True)
        print("Body:", body)
        print("Signature:", signature)
        handler.handle(body, signature)
    except Exception as e:
        print("Webhook Exception:", repr(e))
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def on_message(event):
    handle_text_message(event, line_bot_api)
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))   # 10000 是預設備用值
    app.run(host="0.0.0.0", port=port)
