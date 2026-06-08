# KlearIO MVP Backlog

This backlog is intentionally simple.

The goal is to build a working MVP before adding advanced architecture, agents, or
complex integrations.

Legend: `[x]` done, `[ ]` not done yet.

## Phase 1 - Product framing

### P0

- [x] Define strict MVP scope
- [x] Define supported document types for the first version
- [x] Define the main user journey
- [x] Define the first data model
- [x] Define the first technical stack

### P1

- [x] Define naming rules for documents
- [x] Define folder classification rules
- [x] Define search criteria
- [x] Define minimal UX screens

## Phase 2 - Technical foundation

### P0

- [x] Create frontend application
- [x] Create backend application
- [x] Create local development setup
- [x] Create basic API structure
- [x] Create basic database structure
- [x] Create document upload endpoint
- [x] Create document metadata model

### P1

- [ ] Add simple logging
- [x] Add structured API errors for controlled failures
- [x] Add basic tests
- [x] Add local file storage structure
- [x] Add backend health check

## Phase 3 - Document processing

### P0

- [x] Upload PDF document
- [x] Store original file
- [x] Extract readable text from PDF
- [x] Detect document type using simple rules
- [x] Extract key fields using simple rules
- [x] Generate proposed file name
- [x] Generate proposed folder path
- [x] Save processing result

### P1

- [ ] Add OCR for image-based documents
- [ ] Add direct image or photo upload
- [ ] Add confidence score
- [x] Add manual correction of detected metadata
- [x] Add processing status
- [x] Add human validation status

## Phase 4 - User interface

### P0

- [x] Create upload screen
- [x] Create document processing result screen
- [x] Display detected document type
- [x] Display extracted fields
- [x] Display proposed file name
- [x] Display proposed folder
- [x] Display list of uploaded documents
- [x] Add simple search

### P1

- [x] Add link to open the original PDF
- [x] Add manual validation action
- [x] Add field correction UI
- [x] Add filter by document type
- [x] Add empty states and error states

## Phase 5 - MVP validation

### P0

- [ ] Test with real administrative documents
- [ ] Validate document type detection
- [ ] Validate extraction quality
- [ ] Validate naming rules
- [ ] Validate folder classification
- [ ] Validate search usefulness

### P1

- [ ] Identify weak document types
- [ ] Improve extraction rules
- [ ] Improve UX flow
- [ ] Prepare next technical decisions

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

- No OCR in the current MVP
- No direct image or photo upload
- No authentication in the current MVP
- No cloud storage in the current MVP
- No physical file rename or move yet
- No agentic orchestration
- No complex AI team
- No workflow engine
- No multi-user enterprise mode
- No production-grade cloud architecture at the beginning
- No sensitive healthcare document support
- No legal or tax recommendation
