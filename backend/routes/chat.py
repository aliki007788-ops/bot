from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from backend.routes.chat import router as chat_router
import os

app = FastAPI(title="Eitaa AI Miniapp", version="1.0.0")

# ─── CORS ─────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ───────────────────────────────────
app.include_router(chat_router)

# ─── Static Files ─────────────────────────────
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# ─── صفحه اصلی ────────────────────────────────
@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

@app.head("/")
async def root_head():
    return Response(status_code=200)

# ─── Health Check ─────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
