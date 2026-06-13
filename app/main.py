import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx

load_dotenv()

app = FastAPI()

# Static files y templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_API_URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"


@app.get("/", response_class=HTMLResponse)
async def landing():
    return templates.TemplateResponse("index.html", {"request": {}})


@app.get("/chat", response_class=HTMLResponse)
async def chat_page():
    return templates.TemplateResponse("chat.html", {"request": {}})


@app.post("/api/chat")
async def chat(message: str):
    if not MINIMAX_API_KEY:
        return {"error": "MINIMAX_API_KEY no configurada"}

    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "MiniMax-Text-01",
        "messages": [{"role": "user", "content": message}]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(MINIMAX_API_URL, json=payload, headers=headers, timeout=30)
            data = response.json()
            reply = data.get("choices", [{}])[0].get("message", {}).get("content", "Sin respuesta")
            return {"reply": reply}
        except Exception as e:
            return {"error": str(e)}
