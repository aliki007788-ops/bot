from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.config import client, AI_MODEL, MAX_TOKENS, TEMPERATURE, MAX_HISTORY
from backend.prompts import SYSTEM_PROMPTS
import json

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    category: str
    history: list = []

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        messages = build_messages(request)
        response = client.chat.completions.create(
            model=AI_MODEL, messages=messages, max_tokens=MAX_TOKENS, temperature=TEMPERATURE
        )
        return {"success": True, "response": response.choices[0].message.content}
    except Exception as e:
        print(f"❌ OpenAI Error: {str(e)}")
        return {"success": False, "response": "متاسفم، مشکلی پیش اومد. لطفاً دوباره تلاش کن!"}

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    try:
        messages = build_messages(request)
        def generate():
            stream = client.chat.completions.create(
                model=AI_MODEL, messages=messages, max_tokens=MAX_TOKENS, temperature=TEMPERATURE, stream=True
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    data = json.dumps({"content": delta.content, "done": False}, ensure_ascii=False)
                    yield f"data: {data}\n\n"
            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
    except Exception as e:
        print(f"❌ Stream Error: {str(e)}")
        def error_gen():
            yield f"data: {json.dumps({'content': 'متاسفم، مشکلی پیش اومد!', 'done': True}, ensure_ascii=False)}\n\n"
        return StreamingResponse(error_gen(), media_type="text/event-stream")

def build_messages(request: ChatRequest) -> list:
    messages = [{"role": "system", "content": SYSTEM_PROMPTS.get(request.category, SYSTEM_PROMPTS["general"])}]
    for msg in request.history[-MAX_HISTORY:]:
        if msg.get("role") in ["user", "assistant"]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": request.message})
    return messages
