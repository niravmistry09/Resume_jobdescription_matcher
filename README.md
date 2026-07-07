# AI Resume Matcher

AI Resume Matcher is a full-stack FastAPI application that compares a candidate resume with a job description and returns a structured match analysis.

The app supports resume upload, job description upload, pasted job description text, skill extraction, semantic similarity, weighted scoring, and Gemini-based explanation.

---

## Features

- Resume upload support
- Job description upload support
- Job description copy-paste support
- PDF and TXT parsing
- Text cleaning and normalization
- Rule-based skill extraction without LLM
- Skill taxonomy using `skills.json`
- Sentence embeddings using `BAAI/bge-base-en-v1.5`
- Cosine similarity using scikit-learn
- Configurable weighted scoring
- Gemini API explanation
- Matched skills, missing skills, extra skills
- Improvement suggestions
- Modern responsive frontend

---

## Tech Stack

### Backend

- FastAPI
- Pydantic
- Uvicorn
- python-dotenv

### Frontend

- HTML
- CSS
- JavaScript
- Bootstrap

### AI / NLP

- sentence-transformers
- `BAAI/bge-base-en-v1.5`
- spaCy
- regex
- Gemini API

### Parsing

- pdfplumber
- PyMuPDF

### Similarity and Scoring

- scikit-learn cosine similarity
- custom scoring service

---

## Project Structure

```text
app/
  api/
    dependencies.py
    v1/
      endpoints/
        compare.py
        health.py
      router.py

  application/
    use_cases/
      compare_resume.py

  core/
    config.py
    exceptions.py
    logging.py

  domain/
    entities/
      resume.py
      job_description.py

  infrastructure/
    external/
      cleaner.py
      parser.py
      skill_extractor.py
      skills.json
      embedding_service.py
      similarity_service.py
      scoring_service.py
      explanation_service.py

  prompts/
    resume_explanation_prompt.txt

  schemas/
    compare.py

  web/
    router.py
    static/
      css/
        styles.css
      js/
        app.js
    templates/
      index.html
