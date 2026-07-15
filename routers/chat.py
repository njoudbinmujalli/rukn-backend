
import json

from fastapi import APIRouter, HTTPException

from config import GEMINI_MODEL, client
from models import ChatRequest
from utils import anonymize_text

router = APIRouter(prefix="/api", tags=["chat"])

SYSTEM_PROMPT_TEMPLATE = """أنت مساعد متخصص في شؤون التركات والإرث الشرعي، تعمل لدى منصة ركن.
أجب بالعربية بأسلوب واضح ومبسط. لا تفتي بالمسائل الشرعية المعقدة.
{context_str}
سؤال المستخدم: {message}"""


@router.post("/chat")
async def chat(req: ChatRequest):
    context_str = ""
    if req.context:
        context_str = f"Estate data: {anonymize_text(json.dumps(req.context, ensure_ascii=False))}"

    prompt = SYSTEM_PROMPT_TEMPLATE.format(context_str=context_str, message=req.message)

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return {"reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

