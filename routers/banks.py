"""
Endpoint طبقة البنوك الوهمية (Mock Banking Layer).

يحاكي استدعاء عدة APIs من بنوك مختلفة (كل واحد بشكل رد مختلف)،
يبحث في كل بنك عن العميل المطابق لرقم الهوية المطلوب تحديداً،
يوحّد شكل كل رد عبر bank_normalizer، ويجمعهم بصافي أصول والتزامات
موحد. كل استعلام لبنك يُسجَّل كخطوة منفصلة بسجل التدقيق (audit trail)،
تماماً كأنها استدعاءات API حقيقية منفصلة.

لو رقم الهوية غير موجود عند أي بنك، يرجّع 404.
"""
import json
import os

from fastapi import APIRouter, HTTPException

from database import add_audit_entry
from bank_normalizer import NORMALIZERS

router = APIRouter(prefix="/api", tags=["banks"])

MOCK_BANKS_DIR = os.path.join(os.path.dirname(__file__), "..", "mock_banks")


def load_bank_file(filename: str) -> dict:
    path = os.path.join(MOCK_BANKS_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/banks/{national_id}")
async def get_bank_assets(national_id: str):
    """
    يستعلم (وهمياً) عن كل البنوك المسجلة بحثاً عن رقم الهوية المعطى،
    يوحّد ردودها، ويرجّع صافي الأصول والالتزامات المجمّعة.
    """
    if not NORMALIZERS:
        raise HTTPException(status_code=500, detail="لا توجد بنوك مسجلة")

    banks_result = []
    total_assets = 0.0
    total_liabilities = 0.0

    for filename, normalizer in NORMALIZERS.items():
        try:
            raw = load_bank_file(filename)
        except FileNotFoundError:
            continue

        normalized = normalizer(raw, national_id)

        if normalized is None:
            # هذا البنك ما عنده حساب لصاحب رقم الهوية هذا — نتخطاه بصمت
            continue

        bank_assets = sum(a["balance"] for a in normalized["accounts"])
        bank_liabilities = sum(l["amount"] for l in normalized["liabilities"])
        total_assets += bank_assets
        total_liabilities += bank_liabilities

        banks_result.append(normalized)

        add_audit_entry(
            f"استعلام بنكي — {normalized['bank_name_ar']}",
            f"أصول: SAR {bank_assets:,.2f} — التزامات: SAR {bank_liabilities:,.2f}"
        )

    if not banks_result:
        raise HTTPException(
            status_code=404,
            detail=f"لا توجد بيانات بنكية مسجلة لرقم الهوية {national_id}"
        )

    net_estate = round(total_assets - total_liabilities, 2)

    add_audit_entry(
        "تجميع الأصول البنكية",
        f"{len(banks_result)} بنوك — صافي: SAR {net_estate:,.2f}"
    )

    return {
        "national_id": national_id,
        "banks": banks_result,
        "total_assets": round(total_assets, 2),
        "total_liabilities": round(total_liabilities, 2),
        "net_estate": net_estate,
    }
