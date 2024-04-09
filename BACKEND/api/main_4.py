from fastapi import FastAPI, Request, Response
# from pydantic import BaseModel
from telegram import Update
from telegram.ext import Dispatcher, MessageHandler, Filters
from telegram.ext.webhookcontext import WebhookContext
from telegram.utils.request import Request as TGRequest

app = FastAPI()

# Set up the Telegram bot
BOT_TOKEN=""

REQUEST = TGRequest(connect_timeout=0.5, read_timeout=1.0)
dispatcher = Dispatcher(bot_token=BOT_TOKEN, request=REQUEST)

# Define a webhook endpoint for receiving messages
@app.post("/webhook")
async def telegram_webhook(request: Request, response: Response):
    update = await request.json()
    webhook_context = WebhookContext(update, dispatcher.bot)

    # Pass the update to the dispatcher for processing
    dispatcher.process_update(Update.de_json(update, dispatcher.bot))

    return {"status": "ok"}

# Handle incoming messages
@dispatcher.message_handler(filters=Filters.text)
def echo_message(update: Update, context: WebhookContext):
    text = update.message.text
    chat_id = update.message.chat_id

    context.bot.send_message(chat_id=chat_id, text=f"You said: {text}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
