# KlearIO MVP

KlearIO is a simple document organization assistant.

The MVP focuses on helping users upload administrative documents, detect their type, extract key information, rename them automatically, classify them into folders, and search them easily.

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

The repository now contains a first local prototype skeleton.

The first objective is to build a simple end-to-end prototype where a user can upload one document and receive:

- A detected document type
- Extracted key fields
- A proposed file name
- A proposed folder
- A searchable record

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
- Only text-based PDFs are supported; scanned PDFs need OCR, which is not part of this step.
- Document detection uses simple keyword rules.
- Field extraction uses approximate regex rules.
- Proposed file names and folders are stored as metadata only.
- Files are not physically renamed or moved into the proposed folder yet.
- There is no authentication, cloud storage, agentic workflow, or microservice architecture.
