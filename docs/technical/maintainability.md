# Human Maintainability

## Why It Matters

KlearIO handles administrative documents, business rules, and user-facing decisions.
The code must be easy for a human developer to understand, review, change, and fix,
even if the first version was assisted by AI.

Maintainability is a core project requirement, not a secondary concern.

## Code Principles

- Keep code simple, explicit, and readable.
- Prefer direct logic over clever logic.
- Keep changes small, progressive, and easy to review.
- Avoid abstractions until they remove real duplication or clarify a real boundary.
- Do not optimize code for AI generation at the expense of human understanding.
- A developer should understand the main flow by reading a small number of files.

## Naming Principles

- Use explicit names for files, modules, functions, classes, and variables.
- Prefer names that describe the business role or technical responsibility.
- Avoid vague names such as `helper`, `manager`, `processor`, or `data` unless the
  context makes them precise.
- Keep business concepts visible in names: document type, extracted fields,
  proposed file name, proposed folder, storage path.

## Comments and Docstrings

- Add simple docstrings to important functions.
- Use comments to explain intent, business rules, or non-obvious technical choices.
- Do not comment on obvious code behavior.
- Document known MVP limits when they affect future work or user expectations.
- Keep documentation short and close to the decision it explains.

## Function and File Responsibilities

- Each function should do one main thing.
- Each file should have a clear responsibility.
- Avoid mixing API routing, storage, extraction, classification, naming, and database
  logic in the same place.
- Keep business rules easy to locate and modify.
- Split code only when it improves readability or isolates a real responsibility.

## Architecture Principles

- Keep the MVP and V1 as a modular monolith.
- Do not introduce microservices, Kubernetes, or distributed architecture for the MVP.
- Keep the FastAPI backend organized in simple modules.
- Keep the Next.js frontend readable and avoid unnecessary fragmentation.
- Prepare future evolution without making the current system harder to understand.

## Working With Codex

- Before important changes, propose a short plan and wait for validation.
- After changes, provide the modified files, the role of each change, possible
  impacts, test commands, and priority review points.
- Prefer small changes that a human reviewer can understand quickly.
