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