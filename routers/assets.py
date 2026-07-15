"""
Endpoint جلب أصول وخصوم المتوفى (حالياً بيانات وهمية/mock).
"""
from fastapi import APIRouter

from database import add_audit_entry

router = APIRouter(prefix="/api", tags=["assets"])


@router.get("/assets/{decedent_id}")
async def get_assets(decedent_id: str):
    mock_data = {
        "bank": "مصرف الإنماء",
        "accounts": [
            {"type": "جاري", "balance": 245000, "currency": "SAR"},
            {"type": "ادخار", "balance": 180500, "currency": "SAR"}
        ],
        "total_assets": 2847500,
        "total_liabilities": 320000,
        "net_estate": 2527500,
        "details": {
            "bank_accounts": 518250,
            "real_estate": 2150000,
            "stocks": 112250,
            "vehicles": 67000
        }
    }
    add_audit_entry("جلب الأصول", "مصرف الإنماء — صافي التركة: SAR 2,527,500")
    return mock_data
