# src/mappings.py

reason_mapping = {

    "لايملك رخصة": "لا يملك رخصة قيادة",

    "انتهاء رخصه": "أنتهاء تاريخ رخصة القيادة",
    "رخصة منتهية": "أنتهاء تاريخ رخصة القيادة",

    "عكس السير": "عكس اتجاه السير",

    "الرخصة لا تخول له بالقيادة":
        "نوع الرخصة لا يخوله بقيادة المركبة",

    "إخفاء حقيقة جوهرية / تبديل السائق وقت الحادث":
        "اخفاء حقيقة جوهرية / تبديل السائق وقت الحادث",
}


placeholder_numbers = {

    966,
    966555555555,
    966522222222,
    966505050505

}


# The source system stores Debtor Type with inconsistent casing
# (e.g. "insured" vs "Insured"). This normalizes to a clean, consistent
# label used across every dashboard page.
debtor_type_mapping = {

    "insured": "Insured",
    "Insured": "Insured",
    "third_party": "Third Party",

}


# The source "Status" column mixes an English label with an Arabic
# description in the same cell (e.g. "Approved معلق"). Business logic
# only needs the English label, so this maps the raw value to a clean
# status used for filtering and KPIs.
status_mapping = {

    "Approved معلق": "Approved",
    "Transfer To Law رفض السداد": "Transfer To Law",
    "Collected تم السداد - كامل": "Collected",
    "Closed حذف المسترد": "Closed",
    "Registered جاري التواصل": "Registered",
    "Partial Payment تم السداد - جزئي": "Partial Payment",
    "Delay Payment وعد سداد": "Delay Payment",

}
