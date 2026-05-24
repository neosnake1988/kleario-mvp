import re


DATE_PATTERNS = (
    r"\b(\d{4}-\d{2}-\d{2})\b",
    r"\b(\d{2}/\d{2}/\d{4})\b",
    r"\b(\d{2}-\d{2}-\d{4})\b",
)

AMOUNT_PATTERN = re.compile(
    r"(?:total\s+ttc|amount\s+due|montant\s+(?:dû|du|ttc))\s*:?\s*([0-9]+(?:[,.][0-9]{2})?)",
    re.IGNORECASE,
)

REFERENCE_PATTERN = re.compile(
    r"(?:reference|référence|ref\.?|invoice\s+number|facture\s+n[°o])\s*:?\s*([A-Z0-9_-]+)",
    re.IGNORECASE,
)


def extract_fields(text: str) -> dict[str, str | None]:
    """Extract the first useful fields with simple MVP rules.

    These regex-based rules are intentionally limited. They provide a readable
    first pass that users can later correct when manual editing is added.
    """
    return {
        "issuer": extract_issuer(text),
        "document_date": extract_date(text),
        "amount": extract_amount(text),
        "reference_number": extract_reference_number(text),
    }


def extract_issuer(text: str) -> str | None:
    """Return the first non-empty line as an approximate issuer."""
    for line in text.splitlines():
        cleaned = line.strip()
        if cleaned:
            return cleaned[:120]
    return None


def extract_date(text: str) -> str | None:
    """Find the first date matching one of the supported MVP formats."""
    for pattern in DATE_PATTERNS:
        match = re.search(pattern, text)
        if match:
            return normalize_date(match.group(1))
    return None


def extract_amount(text: str) -> str | None:
    """Find an amount near simple invoice labels such as Total TTC."""
    match = AMOUNT_PATTERN.search(text)
    if not match:
        return None
    return match.group(1).replace(",", ".")


def extract_reference_number(text: str) -> str | None:
    """Find a basic reference or invoice number when a label is present."""
    match = REFERENCE_PATTERN.search(text)
    if not match:
        return None
    return match.group(1)


def normalize_date(value: str) -> str:
    """Normalize supported date formats to YYYY-MM-DD when possible."""
    if "/" in value:
        day, month, year = value.split("/")
        return f"{year}-{month}-{day}"
    if re.match(r"\d{2}-\d{2}-\d{4}", value):
        day, month, year = value.split("-")
        return f"{year}-{month}-{day}"
    return value
