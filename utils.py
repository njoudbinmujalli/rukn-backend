"""
دوال مساعدة عامة (utilities) مستخدمة في أكثر من مكان بالتطبيق.
"""
import re


def anonymize_text(text: str) -> str:
    """
    يخفي المعلومات الشخصية الحساسة قبل إرسال أي نص لجهة خارجية (مثل نموذج الذكاء الاصطناعي):
    - أرقام الهوية الوطنية/الإقامة (10 خانات) → [PERSON_N]
    - أرقام الجوال السعودية (05XXXXXXXX) → [PHONE_N]
    """
    phones = re.findall(r'\b05\d{8}\b', text)
    for i, phone in enumerate(dict.fromkeys(phones)):
        text = text.replace(phone, f"[PHONE_{i+1}]")

    ids = re.findall(r'\b\d{10}\b', text)
    for i, id_num in enumerate(dict.fromkeys(ids)):
        text = text.replace(id_num, f"[PERSON_{i+1}]")

    return text
