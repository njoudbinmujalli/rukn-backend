"""
Endpoint توزيع صافي التركة على الورثة حسب النسب.
"""
from fastapi import APIRouter

from models import DistributeRequest
from database import add_audit_entry

router = APIRouter(prefix="/api", tags=["distribute"])


@router.post("/distribute")
async def distribute(req: DistributeRequest):
    results = []
    for heir in req.heirs:
        amount = round(req.net_estate * heir['percentage'] / 100)
        results.append({
            **heir,
            "amount": amount,
            "account_type": "وصاية مقيّدة" if heir.get('is_minor') else "تحويل مباشر"
        })
        add_audit_entry(f"توزيع — {heir['name']}", f"{heir['share']} = SAR {amount:,}")
    return {"success": True, "distribution": results}
