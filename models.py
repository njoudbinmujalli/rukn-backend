"""
نماذج Pydantic (Request/Response schemas) المستخدمة عبر الـ routers.
"""
from pydantic import BaseModel
from typing import Optional


class DistributeRequest(BaseModel):
    heirs: list
    net_estate: float


class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None


class AgentVerifyRequest(BaseModel):
    agent_id: str
    decedent_id: str
    heirs: list