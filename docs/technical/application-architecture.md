# Application Architecture

## Purpose

KlearIO MVP is a local-first document organization assistant. The architecture must
support the current product loop while staying ready for a future cloud version.

The goal is a simple, robust, maintainable system, not a prematurely distributed
platform.

## Architecture Style

The MVP and V1 use a modular monolith:

- one FastAPI backend;
- one Next.js frontend;
- one local SQLite database;
- one local file storage area.

Microservices, Kubernetes, and a full event-driven architecture are intentionally
out of scope for the MVP.

## Backend

The backend owns document processing and persistence. Its modules should stay small
and explicit:

- API routes receive requests and return responses.
- File storage saves uploaded originals.
- Text extraction reads text from PDFs.
- Document detection classifies documents with simple rules.
- Field extraction extracts key values with readable rules.
- Naming proposes file names and folders.
- Database code stores and searches document records.

Business rules should remain easy to find in the service modules.

## Frontend

The frontend provides the local user experience:

- upload a PDF;
- display the latest processing result;
- list saved documents;
- search existing records.

The Next.js code should remain readable and only be split into more components when
the page becomes hard to scan.

## Data and Storage

SQLite is the MVP database. PostgreSQL is the likely future production database.
Database access should stay isolated enough that this migration does not require
rewriting document processing logic.

Local file storage is the MVP storage backend. Azure Blob Storage is the likely
future object storage target. File storage code should remain behind a clear module
boundary.

## Processing Model

PDF processing is synchronous for now. This keeps the MVP easy to run and debug.

A background worker can be introduced later if document processing becomes slow,
unreliable, or needs retries. The current code should avoid assumptions that would
make that transition difficult.

## Security and Privacy

KlearIO handles private administrative documents. The MVP is local and has no
authentication, but future architecture must prepare for:

- authentication;
- document access control;
- private file storage;
- auditability;
- safer error messages;
- secure cloud configuration.

Security should be added progressively, but document confidentiality must guide
technical choices from the beginning.

## Observability and Operations

The MVP should start with simple diagnostics:

- clear error messages;
- understandable processing steps;
- logs when they become useful;
- simple health checks.

Advanced monitoring should come later, when deployment and usage justify it.

## Evolution Path

The expected evolution path is:

1. Local MVP with FastAPI, Next.js, SQLite, and local file storage.
2. Hardened modular monolith with clearer errors, security boundaries, and tests.
3. Cloud-ready monolith using PostgreSQL and object storage.
4. Background processing for slow or retryable document tasks.
5. More advanced extraction, OCR, AI assistance, and observability when justified.
