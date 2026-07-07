# Architecture Notes

The application uses a clean, layered structure to keep HTTP concerns, orchestration, and infrastructure adapters separate.

## Dependency Rule

Outer layers may depend on inner layers. Use cases coordinate infrastructure services through explicit construction in `app/api/dependencies.py`, while API endpoints stay thin.

```text
web/api -> application/use_cases -> infrastructure/external
domain/entities -> shared business data structures
```

## Layer Responsibilities

- API: request parsing, response mapping, HTTP status codes, dependency injection.
- Application: orchestration of the resume comparison workflow.
- Infrastructure: parsing, cleaning, skill extraction, embeddings, similarity, scoring, and Gemini explanation adapters.
- Domain: core resume and job description entities.
- Web: server-rendered page and static frontend assets.

## Current Flow

```text
Upload files
  -> parse PDF/TXT
  -> clean extracted text
  -> extract skills
  -> generate embeddings
  -> calculate semantic similarity
  -> calculate weighted score
  -> optionally generate Gemini explanation
  -> return structured JSON
```

## Current Limits

- Supported uploads are PDF and TXT.
- DOC/DOCX support is intentionally not present yet.
- First embedding use may require downloading `BAAI/bge-base-en-v1.5`.
- Gemini explanation requires `GEMINI_API_KEY`.
