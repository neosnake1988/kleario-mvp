# KlearIO MVP Technical Stack

## Technical objective

The MVP should be simple to build, simple to run, and simple to understand.

The goal is not to build the final scalable architecture immediately.

The goal is to create a working end-to-end product loop.

## Recommended MVP stack

## Frontend

Recommended:

- Next.js
- React
- TypeScript

Reason:

- Good developer experience
- Easy routing
- Good UI structure
- Can evolve into a production frontend later
- Works well with modern AI coding tools

## Backend

Recommended:

- FastAPI
- Python

Reason:

- Simple API development
- Good fit for document processing
- Easy integration with OCR and AI libraries
- Easy to understand
- Good OpenAPI support

## Database

Initial MVP:

- SQLite

Later:

- PostgreSQL

Reason:

- SQLite is enough for local MVP development
- PostgreSQL can be introduced later without changing the whole product logic

## File storage

Initial MVP:

- Local file storage

Later:

- Azure Blob Storage

Reason:

- Local storage is faster for early prototyping
- Azure Blob Storage will be more appropriate for cloud deployment later

## OCR

Initial options:

- PyMuPDF for text-based PDF extraction
- Tesseract for OCR
- Azure Document Intelligence later if needed

Recommended first step:

- Extract text from PDF first
- Add OCR only when needed

Reason:

- Many PDFs already contain readable text
- OCR adds complexity
- The MVP should prove the workflow before optimizing extraction quality

## Document intelligence

Initial MVP:

- Rule-based detection
- Rule-based extraction

Later:

- LLM-assisted classification
- LLM-assisted extraction
- Azure Document Intelligence
- Hybrid rules and AI

Reason:

- Rules are easier to test and debug
- AI should be added where rules are not enough
- The first MVP should remain transparent

## Search

Initial MVP:

- Simple SQL search on metadata and extracted text

Later:

- Full-text search
- Vector search
- Semantic search

Reason:

- Simple search is enough to validate the first use case
- Advanced search can be added once enough documents exist

## Authentication

Initial MVP:

- No authentication for local prototype

Later:

- Basic authentication
- OAuth
- User accounts

Reason:

- Authentication is not needed to validate the first document processing loop locally
- Security will become mandatory before any real user or hosted environment

## Suggested local architecture

    Frontend Next.js
            |
            | HTTP API
            v
    Backend FastAPI
            |
            | Reads / writes
            v
    SQLite database
            |
            | Stores files
            v
    Local storage

## Suggested repository structure

    kleario-mvp/
    ├── app/
    │   ├── frontend/
    │   └── backend/
    ├── docs/
    │   ├── product/
    │   ├── technical/
    │   └── decisions/
    ├── tests/
    ├── README.md
    └── MVP_BACKLOG.md

## Backend first modules

The backend should start with simple modules:

    backend/
    ├── main.py
    ├── api/
    │   └── documents.py
    ├── services/
    │   ├── file_storage.py
    │   ├── text_extraction.py
    │   ├── document_detection.py
    │   ├── field_extraction.py
    │   └── naming.py
    ├── models/
    │   └── document.py
    └── database/
        └── db.py

## Frontend first screens

The frontend should start with:

- Upload page
- Document result page
- Document list page
- Simple search

## Development principles

- Keep code readable
- Use explicit names
- Avoid unnecessary abstraction
- Avoid premature optimization
- Keep modules small
- Write simple tests
- Prefer understandable logic
- Document important decisions

## Not for the MVP

Do not introduce these too early:

- Kubernetes
- Microservices
- Event-driven architecture
- Complex agent orchestration
- Advanced cloud deployment
- Complex authentication
- Complex permissions
- Enterprise workflow engine
- Long-term memory
- Third-party API ecosystem