
## 🚀 Features

*   **PDF Text Extraction:** Built-in parsers using `PyMuPDF` and `pdfplumber`.
*   **Semantic Similarity:** Computes embedding vectors using the `BAAI/bge-base-en-v1.5` transformer model via PyTorch to accurately match concepts, not just keywords.
*   **AI Explanations:** Powered by `google-genai` using the latest `gemini-2.5-flash` model to give structured insights (strengths, gaps, suggestions) on why a candidate fits or doesn't fit the role.
*   **Modern Web UI:** Simple UI components embedded directly inside the FastAPI ecosystem.
*   **Production Ready:** Full structured logging with crash-protection filters and unit/integration testing suite using `pytest`.

---

## 📂 Project Structure

```text
RESUME_JOBDESCRIPTION_MATCHER/
├── app/
│   ├── api/            # Route endpoints & API versioning v1
│   ├── application/    # Core business use cases
│   ├── core/           # Config setups, logging configurations, exceptions
│   ├── domain/         # Core business logic models
│   ├── infrastructure/ # External services (Gemini Client, Embeddings Engine)
│   ├── prompts/        # System prompts for LLM tuning
│   ├── schemas/        # Pydantic validation schemas
│   └── web/            # HTML templates and static UI assets
├── docs/               # System architecture design notes
├── tests/              # Unit & Integration test pipelines
├── .env.example        # Environment blueprint
└── requirements.txt    # Project dependencies

🛠️ Setup Instructions

1. Prerequisites
Ensure you have Python 3.10+ installed on your system.


2. Clone and Setup Environment

# Initialize virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate


3. Install Dependencies

pip install -r requirements.txt
python -m spacy download en_core_web_sm


4. Configuration
Create a .env file in the root directory (copy from .env.example):


GEMINI_API_KEY=your_actual_google_ai_studio_api_key
APP_ENV=development
APP_DEBUG=True

⚡ Running the Application
To start the FastAPI production-ready development server with auto-reload:

python -m uvicorn app.main:app --reload

🧪 Testing:
The repository includes structured unit and integration tests. To run the automated validation tests:

pytest
        styles.css
      js/
        app.js
    templates/
      index.html
