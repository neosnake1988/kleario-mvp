# Decision Log

This file tracks important product and technical decisions.

## Decision format

Each decision should use this structure:

    ## YYYY-MM-DD — Decision title

    ### Context

    Explain the situation.

    ### Decision

    Explain the decision.

    ### Rationale

    Explain why this decision was made.

    ### Consequences

    Explain what this decision implies.

## 2026-05-18 — Start with a simple MVP workspace

### Context

The project has a broader long-term agentic vision, but starting directly with a full agentic architecture would add too much complexity before validating the product.

### Decision

Create a dedicated MVP workspace focused on building the core product manually and pragmatically.

### Rationale

The first goal is to validate the core document upload, classification, extraction, renaming, storage, and search flow.

### Consequences

The MVP will not use a full agentic architecture at the beginning.

Agentic logic may be introduced later if the product flow is validated.

## 2026-06-07 - Consolidate the MVP architecture as a modular monolith

### Context

The local prototype can upload PDFs, extract text, classify documents, extract key
fields, propose names and folders, store files locally, and save records in SQLite.
Before adding more features, the project needs clear architecture rules that keep
the code understandable and ready for gradual cloud evolution.

### Decision

Keep the MVP and V1 as a modular monolith:

- FastAPI backend with simple modules;
- Next.js frontend with limited fragmentation;
- SQLite and local file storage for the local MVP;
- PostgreSQL as the likely future production database;
- Azure Blob Storage as the likely future object
  storage target;
- synchronous PDF processing for now, with background workers introduced only when
  processing time, retries, or reliability require them.

Do not introduce microservices, Kubernetes, or a full event-driven architecture for
the MVP.

### Rationale

The current product loop is small enough to keep in one application. A modular
monolith keeps development, testing, debugging, and review simple while preserving
clear replacement points for database, storage, security, and processing changes.

### Consequences

Architecture work should focus on clear module boundaries, human maintainability,
document privacy, understandable errors, and progressive hardening. Future cloud
work should extend these boundaries instead of replacing the whole application.

The current MVP stores proposed file names and folders as metadata. Physical file
renaming or moving can be added later without changing the core product flow.
