# main.py
# https://www.freecodecamp.org/news/how-to-build-and-deploy-python-telegram-bot-v20-webhooks/

from contextlib import asynccontextmanager
from http import HTTPStatus
from telegram import Update
from telegram.ext import Application, CommandHandler
from telegram.ext._contexttypes import ContextTypes
from fastapi import FastAPI, Request, Response


TELEGRAM_TOKEN="6635051450:AAE288gRD9RjA8y4wzLiwYgRmJq1mYklzHo"
webhook_url= 'https://edu202415.aacom.net:8443/pushin'

# Initialize python telegram bot
ptb = (
    Application.builder()
    .updater(None)
    .token(TELEGRAM_TOKEN)
    .read_timeout(7)
    .get_updates_read_timeout(42)
    .build()
)

@asynccontextmanager
async def lifespan(_: FastAPI):
    await ptb.bot.setWebhook(webhook_url)
    async with ptb:
        await ptb.start()
        yield
        await ptb.stop()

# Initialize FastAPI app (similar to Flask)
app = FastAPI(lifespan=lifespan)

@app.post("/")
async def process_update(request: Request):
    req = await request.json()
    update = Update.de_json(req, ptb.bot)
    await ptb.process_update(update)
    return Response(status_code=HTTPStatus.OK)

# Example handler
async def start(update, _: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text("starting...")

ptb.add_handler(CommandHandler("start", start))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)