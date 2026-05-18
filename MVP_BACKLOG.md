# KlearIO MVP Backlog

This backlog is intentionally simple.

The goal is to build a working MVP before adding advanced architecture, agents, or complex integrations.

## Phase 1 — Product framing

### P0

- Define strict MVP scope
- Define supported document types for the first version
- Define the main user journey
- Define the first data model
- Define the first technical stack

### P1

- Define naming rules for documents
- Define folder classification rules
- Define search criteria
- Define minimal UX screens

## Phase 2 — Technical foundation

### P0

- Create frontend application
- Create backend application
- Create local development setup
- Create basic API structure
- Create basic database structure
- Create document upload endpoint
- Create document metadata model

### P1

- Add simple logging
- Add basic error handling
- Add basic tests
- Add local file storage structure

## Phase 3 — Document processing

### P0

- Upload PDF document
- Store original file
- Extract readable text from PDF
- Detect document type using simple rules
- Extract key fields using simple rules
- Generate proposed file name
- Generate proposed folder path
- Save processing result

### P1

- Add OCR for image-based documents
- Add confidence score
- Add manual correction of detected metadata
- Add processing status

## Phase 4 — User interface

### P0

- Create upload screen
- Create document processing result screen
- Display detected document type
- Display extracted fields
- Display proposed file name
- Display proposed folder
- Display list of uploaded documents
- Add simple search

### P1

- Add document preview
- Add manual validation screen
- Add field correction UI
- Add filter by document type
- Add empty states and error states

## Phase 5 — MVP validation

### P0

- Test with real administrative documents
- Validate document type detection
- Validate extraction quality
- Validate naming rules
- Validate folder classification
- Validate search usefulness

### P1

- Identify weak document types
- Improve extraction rules
- Improve UX flow
- Prepare next technical decisions

## First supported document types

Initial candidates:

- Invoice
- Tax document
- Insurance document
- Bank document
- Payslip
- Administrative letter
- Contract
- Identity-related document

The MVP should start with only a few of them if needed.

## Non-goals for now

- No agentic orchestration
- No complex AI team
- No workflow engine
- No multi-user enterprise mode
- No production-grade cloud architecture at the beginning
- No sensitive healthcare document support
- No legal or tax recommendation