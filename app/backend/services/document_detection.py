# These keyword lists are intentionally small and explicit for the MVP.
# They should stay easy to read before introducing more advanced detection.
INVOICE_KEYWORDS = (
    "facture",
    "invoice",
    "total ttc",
    "amount due",
    "montant dû",
    "montant du",
)

TAX_KEYWORDS = ("avis d'imposition", "impôt", "impot", "taxe", "tax")
INSURANCE_KEYWORDS = ("assurance", "contrat d'assurance", "attestation")


def detect_document_type(text: str) -> str:
    """Detect a document type with simple keyword rules.

    This is deliberately approximate for the MVP. The order matters: invoice
    rules are checked first because invoices are the first supported use case.
    """
    normalized = text.lower()
    if any(keyword in normalized for keyword in INVOICE_KEYWORDS):
        return "invoice"
    if any(keyword in normalized for keyword in TAX_KEYWORDS):
        return "tax_document"
    if any(keyword in normalized for keyword in INSURANCE_KEYWORDS):
        return "insurance_document"
    return "unknown"
