from fastapi import APIRouter
from models import AgentVerifyRequest
from database import add_audit_entry

router = APIRouter(prefix="/api", tags=["verify"])

@router.post("/verify-agent")
async def verify_agent(data: AgentVerifyRequest):
    heir_ids = [h.get('national_id', '') for h in data.heirs]
    
    if data.agent_id in heir_ids:
        add_audit_entry("تحقق الوكيل", f"تم التحقق من هوية الوكيل بنجاح")
        return {"verified": True, "message": "تم التحقق من هويتك كوريث معتمد ✅"}
    else:
        return {"verified": False, "message": "رقم هويتك غير موجود في قائمة الورثة"}