"""
Endpoints قراءة سجل الـ audit log والتحقق من سلامة سلسلة الـ hash.
"""
import hashlib
import json

from fastapi import APIRouter

from database import fetch_all_logs

router = APIRouter(prefix="/api", tags=["audit"])


@router.get("/audit")
async def get_audit():
    rows = fetch_all_logs()
    return {
        "logs": [
            {
                "id": r[0], "action": r[1], "detail": r[2],
                "timestamp": r[3], "prev_hash": r[4], "hash": r[5]
            } for r in rows
        ]
    }


@router.get("/audit/verify")
async def verify_audit():
    rows = fetch_all_logs()
    prev_hash = "0" * 64
    for i, row in enumerate(rows):
        payload = json.dumps({
            "action": row[1], "detail": row[2],
            "timestamp": row[3], "prev_hash": row[4]
        })
        expected = hashlib.sha256(payload.encode()).hexdigest()
        if expected != row[5] or row[4] != prev_hash:
            return {"valid": False, "broken_at": i + 1}
        prev_hash = row[5]
    return {"valid": True, "total_logs": len(rows)}
