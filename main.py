"""
نقطة تشغيل التطبيق: إنشاء الـ FastAPI app، إعداد الـ middleware،
تهيئة قاعدة البيانات، وربط كل الـ routers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routers import ocr, assets, distribute, audit, chat, banks, verify

app = FastAPI(title="Rukn API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()

app.include_router(ocr.router)
app.include_router(assets.router)
app.include_router(distribute.router)
app.include_router(audit.router)
app.include_router(chat.router)
app.include_router(banks.router)
app.include_router(verify.router)

@app.get("/")
async def root():
    return {"message": "Rukn API is running"}
