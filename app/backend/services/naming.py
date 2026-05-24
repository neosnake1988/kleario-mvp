from pathlib import Path


def build_proposed_file_name(
    document_type: str,
    original_file_name: str,
    issuer: str | None,
    document_date: str | None,
    amount: str | None,
) -> str:
    """Build a proposed file name without renaming the stored file."""
    stem = Path(original_file_name).stem
    date_part = document_date or "unknown-date"
    issuer_part = slugify(issuer or stem or "unknown-issuer")
    type_part = slugify(document_type)
    amount_part = f"_{amount.replace('.', '-')}" if amount else ""
    return f"{date_part}_{issuer_part}_{type_part}{amount_part}.pdf"


def build_proposed_folder(document_type: str, issuer: str | None) -> str:
    """Build a proposed folder path without moving the stored file."""
    issuer_part = slugify(issuer or "Unknown")
    if document_type == "invoice":
        return f"Finance/Invoices/{issuer_part}"
    if document_type == "tax_document":
        return "Administration/Taxes"
    if document_type == "insurance_document":
        return f"Administration/Insurance/{issuer_part}"
    return "Administration/Unsorted"


def slugify(value: str) -> str:
    """Make a short value safe enough for a proposed file or folder name."""
    cleaned = value.strip().replace(" ", "_")
    allowed = [char for char in cleaned if char.isalnum() or char in "._-"]
    return "".join(allowed)[:80] or "unknown"
