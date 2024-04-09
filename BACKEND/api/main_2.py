from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from telegram import Update, Filters
from telegram.ext import Updater, MessageHandler, CallbackContext
from queue import Queue

app = FastAPI()

# Define a webhook endpoint for receiving messages
@app.post("/webhook")
async def telegram_webhook(request: Request, response: Response):
    update = await request.json()
    dispatcher.process_update(Update.de_json(update, bot))

    return {"status": "ok"}

# Handle incoming messages
def echo_message(update: Update, context: CallbackContext):
    text = update.message.text
    chat_id = update.message.chat_id

    context.bot.send_message(chat_id=chat_id, text=f"You said: {text}")

# Set up the Telegram bot
BOT_TOKEN = "YOUR_BOT_TOKEN"
update_queue = Queue()
updater = Updater(BOT_TOKEN, update_queue=update_queue)
dispatcher = updater.dispatcher

# Add message handler
message_handler = MessageHandler(Filters.text & ~Filters.command, echo_message)
dispatcher.add_handler(message_handler)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
