"""
طبقة توحيد بيانات البنوك (Bank Normalizer).

كل بنك بالواقع يرجّع بياناته بشكل مختلف (أسماء حقول مختلفة، تركيب متداخل
بشكل مختلف، إلخ). هذا الملف فيه دالة تحويل مخصصة لكل بنك (adapter)
تبحث عن العميل المطلوب برقم هويته الوطنية داخل رد البنك الخام،
وتحوّل بياناته إلى شكل موحد:

{
    "bank_code": "...",
    "bank_name_ar": "...",
    "accounts": [{"type": "...", "balance": 0.0, "currency": "SAR"}],
    "liabilities": [{"type": "...", "amount": 0.0}]
}

لو العميل غير موجود عند هذا البنك، الدالة ترجّع None.
"""


def normalize_rajhi(raw: dict, national_id: str):
    customer = next(
        (c for c in raw.get("customers", []) if c.get("customer_national_id") == national_id),
        None
    )
    if not customer:
        return None
    return {
        "bank_code": raw["bank_code"],
        "bank_name_ar": raw["bank_name_ar"],
        "accounts": [
            {"type": a["account_type"], "balance": a["balance_sar"], "currency": "SAR"}
            for a in customer.get("accounts", [])
        ],
        "liabilities": [
            {"type": l["loan_type"], "amount": l["outstanding_balance_sar"]}
            for l in customer.get("loans", [])
        ],
    }


def normalize_alinma(raw: dict, national_id: str):
    customer = next(
        (c for c in raw.get("customers", []) if c.get("nationalId") == national_id),
        None
    )
    if not customer:
        return None
    liabilities = [
        {"type": "CREDIT_CARD", "amount": c["outstanding"]}
        for c in customer.get("liabilities", {}).get("creditCards", [])
    ]
    liabilities += [
        {"type": "FINANCING", "amount": f["outstanding"]}
        for f in customer.get("liabilities", {}).get("financing", [])
    ]
    return {
        "bank_code": raw["bankId"],
        "bank_name_ar": raw["bankNameAr"],
        "accounts": [
            {"type": a["accType"], "balance": a["currentBalance"], "currency": a.get("ccy", "SAR")}
            for a in customer.get("accountList", [])
        ],
        "liabilities": liabilities,
    }


def normalize_snb(raw: dict, national_id: str):
    customer = next(
        (c for c in raw.get("customers", []) if c.get("idNumber") == national_id),
        None
    )
    if not customer:
        return None
    return {
        "bank_code": raw["institution"]["code"],
        "bank_name_ar": raw["institution"]["nameAr"],
        "accounts": [
            {
                "type": a["productType"],
                "balance": a["availableBalance"]["amount"],
                "currency": a["availableBalance"].get("currency", "SAR"),
            }
            for a in customer.get("accountDetails", [])
        ],
        "liabilities": [
            {"type": o["obligationType"], "amount": o["remainingAmount"]["amount"]}
            for o in customer.get("obligations", [])
        ],
    }


def normalize_riyad(raw: dict, national_id: str):
    customer = next(
        (c for c in raw.get("customers", []) if c.get("national_id") == national_id),
        None
    )
    if not customer:
        return None
    data = customer.get("data", {})
    return {
        "bank_code": raw["bank"],
        "bank_name_ar": raw["displayName"],
        "accounts": [
            {"type": a["type"], "balance": float(a["balance"]), "currency": a.get("currency_code", "SAR")}
            for a in data.get("accounts", [])
        ],
        "liabilities": [
            {"type": l["type"], "amount": float(l["amount"])}
            for l in data.get("outstanding_liabilities", [])
        ],
    }


# خريطة كل بنك لدالة التوحيد الخاصة فيه
NORMALIZERS = {
    "bank_rajhi.json": normalize_rajhi,
    "bank_alinma.json": normalize_alinma,
    "bank_snb.json": normalize_snb,
    "bank_riyad.json": normalize_riyad,
}
