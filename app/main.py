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
        return {"error": "MINIMAX_API_KEY no configurada. Añádela en las variables de entorno."}

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
            
            if response.status_code != 200:
                return {"error": f"Error de API: código {response.status_code}"}
            
            data = response.json()
            
            # Debug: log response structure if choices is empty
            choices = data.get("choices")
            if not choices:
                return {"error": "Respuesta inválida de MiniMax. Revisa la API key."}
            
            first_choice = choices[0] if choices else {}
            msg = first_choice.get("message", {}) if isinstance(first_choice, dict) else {}
            reply = msg.get("content")
            
            if not reply:
                return {"error": "No se recibió contenido en la respuesta."}
            
            return {"reply": reply}
            
        except httpx.TimeoutException:
            return {"error": "Tiempo de espera agotado. Inténtalo de nuevo."}
        except httpx.ConnectError:
            return {"error": "Error de conexión. Verifica tu red."}
        except Exception as e:
            return {"error": f"Error inesperado: {type(e).__name__}"}
