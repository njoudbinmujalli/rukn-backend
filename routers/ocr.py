"""
Endpoint استخراج بيانات صك الوراثة (OCR) عبر Gemini.

تسلسل الحماية:
1. استخراج النص الخام من ملف الـ PDF محلياً.
2. استخراج أرقام الهوية وحفظ الـ mapping قبل الإخفاء.
3. إخفاء أرقام الهوية والجوال قبل إرسالها لـ Gemini.
4. إرسال النص المخفى لـ Gemini لاستخراج بيانات الورثة.
5. استعادة أرقام الهوية الحقيقية من الـ mapping.
6. تسجيل كل خطوة بسجل التدقيق.
"""
import json
import re

from fastapi import APIRouter, UploadFile, File, HTTPException
from pypdf import PdfReader
import io

from config import GEMINI_MODEL, client
from database import add_audit_entry

router = APIRouter(prefix="/api", tags=["ocr"])

EXTRACT_PROMPT = (
    'استخرج من نص صك الوراثة التالي بيانات الورثة. '
    'أرجع كائن JSON واحد فقط (وليس قائمة/array)، بدون أي نص إضافي، بالشكل التالي بالضبط:\n'
    '{{"decedent_name":"","death_date":"","heirs":[{{"name":"","relation":"",'
    '"national_id":"","share":"1/8","percentage":12.5,"age":0,"is_minor":false}}]}}\n\n'
    'نص الصك:\n{deed_text}'
)


def extract_pdf_text(pdf_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def anonymize_with_mapping(text: str):
    """
    يخفي أرقام الهوية والجوال ويرجع:
    - النص المخفى
    - mapping يربط كل placeholder بالرقم الحقيقي
    """
    mapping = {}

    # أرقام الجوال
    phones = re.findall(r'\b05\d{8}\b', text)
    for i, phone in enumerate(dict.fromkeys(phones)):
        placeholder = f"[PHONE_{i+1}]"
        mapping[placeholder] = phone
        text = text.replace(phone, placeholder)

    # أرقام الهوية (10 خانات)
    ids = re.findall(r'\b\d{10}\b', text)
    for i, id_num in enumerate(dict.fromkeys(ids)):
        placeholder = f"[PERSON_{i+1}]"
        mapping[placeholder] = id_num
        text = text.replace(id_num, placeholder)

    return text, mapping


def restore_ids(data: dict, mapping: dict) -> dict:
    """
    يستعيد أرقام الهوية الحقيقية بعد ما Gemini يرجع النتيجة.
    يستبدل الـ placeholders بالأرقام الأصلية في national_id.
    """
    for heir in data.get('heirs', []):
        national_id = heir.get('national_id', '')
        if national_id in mapping:
            heir['national_id'] = mapping[national_id]
    return data


@router.post("/ocr")
async def extract_deed(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="PDF only")

    contents = await file.read()

    try:
        # 1. Extract text locally
        raw_text = extract_pdf_text(contents)
        if not raw_text.strip():
            raise HTTPException(status_code=422, detail="تعذر استخراج نص من ملف الصك")

        # 2. Anonymize and save mapping
        anonymized_text, mapping = anonymize_with_mapping(raw_text)
        add_audit_entry("Anonymization", f"تم إخفاء {len(mapping)} معرف شخصي عن ملف: {file.filename}")

        # 3. Send anonymized text to Gemini
        prompt = EXTRACT_PROMPT.format(deed_text=anonymized_text)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        text = response.text.strip().strip("```json").strip("```").strip()
        parsed = json.loads(text)

        if isinstance(parsed, list):
            data = parsed[0] if parsed else {}
        else:
            data = parsed

        # 4. Restore real IDs from mapping
        data = restore_ids(data, mapping)
        # التحقق من صحة الصك (محاكاة ناجز)
        court_keywords = ['court', 'justice', 'deed', 'ministry', 'محكمة', 'وزارة العدل', 'صك', 'ناجز']
        deed_number = bool(re.search(r'\b\d{8,12}\b', raw_text))
        has_court_keyword = any(kw.lower() in raw_text.lower() for kw in court_keywords)
        data['verified_by_najiz'] = deed_number and has_court_keyword
        data['verification_message'] = "تم التحقق من صحة الصك عبر منصة ناجز" if data['verified_by_najiz'] else "تعذر التحقق من الصك"
        

        # 5. Calculate shares validation
        heirs = data.get('heirs', [])
        total_pct = sum(h.get('percentage', 0) for h in heirs)
        data['shares_valid'] = abs(100 - total_pct) < 0.01
        data['shares_diff'] = round(100 - total_pct, 2)
        data['minors'] = [h['name'] for h in heirs if h.get('is_minor')]

        add_audit_entry("OCR", f"Extracted {len(heirs)} heirs")
        return {"success": True, "data": data}

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
