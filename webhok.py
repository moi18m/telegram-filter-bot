from bot import app
import os

PORT = int(os.environ.get("PORT", 8000))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

if not WEBHOOK_URL:
    raise ValueError("❌ لازم تضيف WEBHOOK_URL داخل متغيرات البيئة")

app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    webhook_url=WEBHOOK_URL
)
