# KlearIO MVP

KlearIO is a simple document organization assistant.

The MVP focuses on helping users upload administrative documents, detect their type,
extract key information, propose a clear file name and folder, and search them easily.

## MVP goal

The goal of this MVP is to validate the core user flow:

1. Upload a document
2. Read the document content
3. Detect the document type
4. Extract key fields
5. Propose a clear file name
6. Propose a target folder
7. Store the document
8. Search for it later

## MVP principles

- Keep the product simple
- Prioritize usability over technical complexity
- Avoid over-engineering
- Keep the code easy to understand
- Build a working flow before optimizing
- Prefer explicit logic over magic
- Add AI only where it brings clear value

## Out of scope for the MVP

The following features are intentionally excluded from the first MVP:

- Bank account connection
- Gmail or Outlook integration
- Registered mail
- Legal or tax advice
- Healthcare sensitive document handling
- Electronic signature
- Complex enterprise workflow
- Full agentic architecture
- Advanced long-term memory
- Third-party API ecosystem

## Initial technical direction

The MVP will start with a simple local-first architecture:

- Frontend: React / Next.js
- Backend: FastAPI
- Database: SQLite first, PostgreSQL later
- File storage: Local storage first, Azure Blob Storage later
- OCR: Tesseract or Azure Document Intelligence depending on complexity
- Search: Simple database search first

## Repository structure

    kleario-mvp/
    ├── app/
    ├── docs/
    │   ├── decisions/
    │   ├── product/
    │   └── technical/
    ├── tests/
    ├── README.md
    └── MVP_BACKLOG.md

## Current status

The repository contains a working local MVP prototype.

Implemented capabilities:

- Upload text-based PDF files.
- Extract readable text from PDF files.
- Classify documents with simple rules.
- Extract basic fields such as issuer, date, amount, and reference number.
- Propose a file name and folder without physically renaming or moving the file.
- Store the original PDF locally and save metadata in SQLite.
- List, search, refresh, and filter documents in the frontend.
- Manually correct document metadata.
- Mark a reviewed document as validated.
- Open the original PDF from the interface without exposing the local file path.
- Return structured API errors for controlled backend failures.

## Architecture docs

- `docs/technical/application-architecture.md`
- `docs/technical/current-mvp-flow.md`
- `docs/technical/maintainability.md`

## Local development

### Backend

From the repository root:

```powershell
cd app\backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

The backend runs on `http://localhost:8000` by default.

Local files are stored under `app/backend/storage/originals`.
The SQLite database is stored under `app/backend/data/kleario.sqlite3`.

### Frontend

From the repository root:

```powershell
cd app\frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:3000` by default and calls the backend
at `http://localhost:8000`. This can be changed with `NEXT_PUBLIC_API_BASE_URL`.

## Current prototype limits

- Only PDF upload is supported.
- Only text-based PDFs are supported.
- OCR is not implemented.
- Direct image or photo upload is not supported.
- Document detection uses simple keyword rules.
- Field extraction uses approximate regex rules.
- Proposed file names and folders are stored as metadata only.
- Files are not physically renamed or moved into the proposed folder.
- There is no authentication, cloud storage, agentic workflow, or microservice architecture.
