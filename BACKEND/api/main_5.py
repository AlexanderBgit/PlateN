import httpx
from fastapi import FastAPI, Request
from pathlib import Path
from dotenv import load_dotenv
import os

# https://salaivv.com/2023/01/04/telegram-bot-fastapi

BASE_DIR = Path(__file__).resolve().parent.parent
env_file = BASE_DIR.parent.joinpath("deploy").joinpath(".env")
if env_file.exists():
    load_dotenv(env_file)
else:
    print("ENV file not found:", env_file)

TOKEN = os.getenv("TELEGRAM_TOKEN", "")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

client = httpx.AsyncClient()

app = FastAPI()

@app.post("/webhook/")
async def webhook(req: Request):
    data = await req.json()
    chat_id = data['message']['chat']['id']
    text = data['message']['text'] + " :)"

    await client.get(f"{BASE_URL}/sendMessage?chat_id={chat_id}&text={text}")

    return data

@app.post("/start/")
async def webhook(req: Request):
    data = await req.json()
    chat_id = data['message']['chat']['id']
    text = data['message']['text'] + " start :)"

    await client.get(f"{BASE_URL}/sendMessage?chat_id={chat_id}&text={text}")

    return data


@app.post("/pushin/")
async def webhook(req: Request):
    data = await req.json()
    chat_id = data['message']['chat']['id']
    text = data['message']['text'] + " pushin :)"

    await client.get(f"{BASE_URL}/sendMessage?chat_id={chat_id}&text={text}")

    return data

@app.post("/pushout/")
async def webhook(req: Request):
    data = await req.json()
    chat_id = data['message']['chat']['id']
    text = data['message']['text'] + " pushout :)"

    await client.get(f"{BASE_URL}/sendMessage?chat_id={chat_id}&text={text}")

    return data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)