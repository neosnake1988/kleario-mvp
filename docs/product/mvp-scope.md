# KlearIO MVP Scope

## Product vision

KlearIO helps users organize administrative documents without having to manually
choose names, folders, and search terms for every file.

The product should feel simple, clear, and calm.

The user should not need to understand document management, OCR, AI, folders, metadata, or classification logic.

## MVP problem

People receive many administrative documents and often do not know how to name them, where to store them, or how to find them later.

The MVP must solve this basic problem:

> KlearIO understands what it is, proposes a clear name and folder, and makes it searchable.

## MVP user promise

For the MVP, KlearIO should be able to:

- Accept a document upload
- Read the document content
- Identify the document type
- Extract a few important fields
- Propose a clear file name
- Propose a logical folder
- Store the document
- Allow simple search

## Primary user journey

1. The user opens KlearIO
2. The user uploads a document
3. KlearIO processes the document
4. KlearIO displays the result
5. The user sees the detected document type
6. The user sees the extracted fields
7. The user sees the proposed name and folder
8. The user validates or corrects the result
9. The document is saved
10. The user can find it later through search

## MVP input formats

The current MVP supports:

- Text-based PDF files.

The current MVP does not support scanned PDFs, direct image or photo upload, or
Word files. OCR can be added later when it becomes necessary.

## MVP output

For each uploaded document, KlearIO should produce:

- Original file
- Extracted text
- Document type
- Key fields
- Proposed file name
- Proposed folder
- Processing status
- Creation date
- Update date

The API exposes only safe public metadata by default. Internal storage paths and
full extracted text are not returned in list, search, upload, read, or update
responses.

## Example output

    {
      "document_type": "invoice",
      "issuer": "EDF",
      "document_date": "2026-05-12",
      "amount": "82.45",
      "proposed_file_name": "2026-05-12_EDF_invoice_82-45.pdf",
      "proposed_folder": "Finance/Invoices/EDF",
      "status": "processed"
    }

## MVP document types

The first version may support a limited list:

- Invoice
- Insurance document
- Tax document
- Bank document
- Payslip
- Administrative letter
- Contract

The first technical prototype can start with invoices only if needed.

## Detection strategy

The MVP should start with simple and understandable rules.

Example rules:

- If the document contains "facture", "invoice", "total TTC", or "amount due", classify it as invoice
- If the document contains "avis d'imposition" or "impôt", classify it as tax document
- If the document contains "assurance", "contrat d'assurance", or "attestation", classify it as insurance document

AI can be added later if rule-based detection becomes too limited.

## Extraction strategy

The MVP should extract only useful fields.

Examples:

- Issuer
- Date
- Amount
- Reference number
- Recipient name
- Due date
- Contract number

The MVP does not need perfect extraction at first.

It needs a clear flow where the user can understand and correct the result.

## UX principles

The interface should be:

- Simple
- Minimal
- Reassuring
- Fast to understand
- Clear about what was detected
- Clear when confidence is low
- Easy to correct

The user should never feel trapped by an automatic decision.

## MVP success criteria

The MVP is successful if:

- A user can upload a PDF
- The document is stored
- Text is extracted
- A document type is proposed
- A file name is proposed
- A folder is proposed
- The physical file does not need to be renamed or moved yet
- The result can be corrected
- The result can be marked as validated after human review
- The document can be found later
- The original PDF can be opened from the interface without exposing a local path

## Current implemented scope

The current MVP supports text-based PDF upload, local file storage, SQLite
metadata storage, simple rule-based classification, simple field extraction,
manual metadata correction, human validation, list/search/filter, and opening the
original PDF from the frontend.

It does not include OCR, direct image/photo upload, authentication, cloud storage,
or physical renaming/moving of files.

## Explicitly out of scope

The MVP does not include:

- OCR
- Direct image or photo upload
- Authentication
- Cloud storage
- Physical file rename or move
- Bank connection
- Email connection
- Registered mail
- Legal advice
- Tax advice
- Medical document workflows
- Electronic signature
- Enterprise validation workflow
- Multi-tenant SaaS complexity
- Advanced agentic architecture
- Complex memory system
