# Cardiometabolic Clinical Guideline Copilot

## 1. Project purpose

This project is an evidence-grounded clinical decision-support application for **licensed healthcare professionals**. It takes either structured patient data or a natural-language clinical question, retrieves relevant clinical-guideline passages, and returns a structured assessment with treatment options, safety warnings, citations, and follow-up questions.

It is intended to support—not replace—clinical judgement, local protocols, medication reconciliation, specialist consultation, or emergency care.

## 2. Clinical scope

The user interface and structured patient form are most developed for **cardiometabolic care**:

- Endocrinology / diabetology: type 2 diabetes, HbA1c targets, obesity, diabetes complications.
- Cardiology: ASCVD, hypertension, dyslipidemia, and heart failure.
- Nephrology: CKD, eGFR/UACR assessment, renal dosing, and nephroprotection.
- Primary care / internal medicine: multimorbidity across diabetes, cardiovascular disease, and CKD.

The indexed knowledge base also contains material for:

- Pulmonology: COPD and asthma (GOLD/GINA).
- Infectious disease and critical care: sepsis, community-acquired pneumonia, and UTIs (IDSA/Sepsis guidance).
- Clinical pharmacy: drug formulary, renal dosing, interactions, and selected warnings.
- Neurology / endocrinology: diabetic neuropathy and related diabetes complications.

Although retrieval can cover these broader topics, the dedicated patient form and the LLM system prompt remain cardiometabolic-focused. Broader specialty use should therefore be validated before clinical deployment.

## 3. Main capabilities

1. **Patient Parameter Analyzer**
   - Accepts information such as age, sex, HbA1c, eGFR, UACR, blood pressure, LVEF, ASCVD/HF/CKD history, current medicines, allergies, and clinical notes.
   - Builds a clinical query and generates a guideline-grounded response.

2. **Clinical Guideline Q&A**
   - Lets clinicians ask a free-text clinical question.
   - Retrieves guideline content and responds in the same structured format.

3. **Evidence and safety presentation**
   - First-line and add-on medication options.
   - Renal/organ-function adjustments.
   - Contraindications and red flags.
   - Guideline citations and excerpts.
   - Follow-up questions for missing information that could affect therapy.

4. **Retrieval evaluation**
   - Includes benchmark cases across cardiology, nephrology, pulmonology, infectious disease, pharmacology, endocrinology, and neurology.

## 4. Architecture

```text
React + Vite frontend
        |
        | HTTP POST requests
        v
FastAPI backend (/api)
        |
        v
ClinicalRAGEngine
        |
        +--> Weaviate hybrid search (BM25 + vector similarity)
        |       |
        |       v
        |   Guideline chunks and parent section context
        |
        +--> OpenAI-compatible LLM endpoint
                |
                v
        Structured clinical JSON response
```

### Frontend

Location: `frontend/`

- React 19, TypeScript, Vite, and Lucide icons.
- `src/App.tsx` controls the two workflows, sends requests to the backend, and renders the response.
- Components render the patient form, question interface, recommendations, and citations.
- The application calls `http://localhost:8000/api` during local development.
- If the backend is unavailable, the frontend currently generates a **demonstration fallback** response. This fallback is not retrieved from the guideline store and must not be treated as live clinical decision support.

### Backend

Location: `backend/app/`

- FastAPI application in `main.py`.
- API endpoints in `api/routes.py`.
- Pydantic input/output models in `engine/schema.py`.
- RAG orchestration and LLM prompt in `engine/clinical_rag.py`.
- Weaviate retrieval in `retrieval/weaviate_retriever.py`.
- Guideline parsing, embedding, and indexing in `ingestion/`.

### Vector database and retrieval

The project stores guideline chunks in a Weaviate Cloud collection named `CardioMetabolicGuidelineChunk` by default.

- Guidelines are parsed into small recommendation-level chunks.
- Every child chunk keeps metadata such as guideline name, chapter, section, evidence level, recommendation ID, target conditions, and table status.
- Each chunk includes its larger parent-section text. Retrieval returns both the precise match and surrounding context (“small-to-big” retrieval).
- Search is hybrid: BM25 keyword search plus a 384-dimensional vector query, using `alpha=0.65`.
- `FastGuidelineEmbedder` uses a local deterministic `HashingVectorizer`; despite the `sentence-transformers` dependency in `requirements.txt`, this code path does not download or use a sentence-transformer model.

### LLM generation

The backend submits the clinician question, patient context, and retrieved guideline excerpts to an OpenAI-compatible chat-completions endpoint. It requests JSON matching `ClinicalAnalysisResponse`, containing:

- Executive summary and patient stratification.
- First-line and add-on medication recommendations.
- Dose/renal rules and warnings.
- Contraindications and red flags.
- Guideline citations.
- Targeted questions for missing data.

The system prompt instructs the model to ground recommendations in retrieved ADA, ACC/AHA/HFSA, and KDIGO excerpts, with specific safeguards for metformin, SGLT2 inhibitors, GLP-1 receptor agonists, and heart failure risks.

## 5. Guideline sources

Raw Markdown guideline data lives in `data/raw_guidelines/`.

| Source group | Included content |
| --- | --- |
| ADA 2024 | Glycemic targets, obesity/weight, pharmacology, cardiovascular disease, neuropathy/retinopathy |
| ACC/AHA 2023 | Heart failure, hypertension, and lipids |
| KDIGO 2023 | CKD and diabetes-related kidney care |
| GOLD & GINA 2024 | COPD and asthma |
| IDSA / Sepsis guidance 2024 | Sepsis, pneumonia, and infectious-disease protocols |
| WHO/FDA formulary | Dosing, interactions, and medication warnings |

These source files are project data, not a guarantee that every guideline is complete, current, locally applicable, or independently verified.

## 6. API

All routes use the `/api` prefix.

### `GET /api/health`

Returns a basic service-status JSON response.

### `POST /api/analyze-patient`

Accepts a `PatientParameters` JSON object. The backend derives a cardiometabolic case summary from supplied values, retrieves guidelines, and produces a structured analysis.

Example request body:

```json
{
  "age": 64,
  "hba1c": 8.5,
  "egfr": 35,
  "uacr": 150,
  "blood_pressure": "145/88",
  "lvef": 35,
  "has_ascvd": true,
  "has_heart_failure": true,
  "has_ckd": true,
  "current_medications": ["metformin"],
  "clinical_notes": "Review cardiorenal therapy."
}
```

### `POST /api/query`

Accepts a free-text `query` and optional `patient_context` object.

```json
{
  "query": "What guideline-supported options apply for a patient with diabetes, CKD, and heart failure?",
  "patient_context": { "egfr": 35, "has_heart_failure": true }
}
```

## 7. Configuration

Create a `.env` file in the project root with values for the remote services:

```env
WEAVIATE_URL=https://your-cluster.weaviate.network
WEAVIATE_API_KEY=your-weaviate-api-key
LLM_API_KEY=your-llm-api-key
LLM_MODEL=qwen/qwen3.8-27b
LLM_BASE_URL=https://openrouter.ai/api/v1
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

`LLM_MODEL`, `LLM_BASE_URL`, and `EMBEDDING_MODEL` have code defaults. The Weaviate URL, Weaviate key, and LLM key must be supplied for the live backend workflow.

Never commit `.env` files or API keys.

## 8. Local setup and run

### Backend

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend serves the API on port 8000. If a production frontend build exists in `frontend/dist`, FastAPI also serves it at the root URL.

### Frontend development server

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

To build the frontend for FastAPI to serve:

```powershell
cd frontend
npm run build
```

## 9. Ingesting or refreshing guideline content

1. Add or update Markdown guideline files in `data/raw_guidelines/`.
2. Verify their section and recommendation formatting so the hierarchical chunker can extract useful recommendation units.
3. Configure Weaviate credentials in `.env`.
4. Run:

```powershell
python backend/app/ingestion/weaviate_indexer.py
```

Important: `create_schema(recreate=True)` currently deletes **every existing collection visible to the configured Weaviate account** before creating the project collection. Review and change this behavior before using an account that contains unrelated collections or production data.

## 10. Evaluation

The `eval/` directory provides a retrieval-oriented benchmark runner.

```powershell
python eval/evaluate_benchmark.py
```

It retrieves the top five chunks for each test vignette and calculates source recall/precision, medication-concept recall, contraindication recall, and an F1-style recommendation score. It writes results to `eval/evaluation_report.json`.

The checked-in report contains 10 benchmark cases and reports:

- Mean guideline retrieval recall: **85%**
- Mean recommendation recall: **90%**
- Mean safety/contraindication recall: **85%**
- Mean overall F1 score: **92.6%**

These are internal retrieval/concept-match metrics, not proof of diagnostic accuracy, patient safety, clinical validity, or regulatory readiness.

## 11. Repository map

```text
backend/app/
  api/routes.py                 API endpoints
  engine/clinical_rag.py        Retrieval + LLM orchestration
  engine/schema.py              Request/response models
  ingestion/                    Chunking, embeddings, indexing
  retrieval/                    Weaviate hybrid search
data/raw_guidelines/            Source guideline Markdown files
eval/                           Clinical benchmark runner and results
frontend/src/                   React application and UI components
requirements.txt                Python dependencies
PROJECT_OVERVIEW.md             This document
```

## 12. Current limitations and recommended next steps

- Validate every guideline source, citation, threshold, and recommendation against current primary sources before clinical use.
- Add versioning, provenance, effective-date metadata, and a formal source-review process for guideline files.
- Add authentication, authorization, audit logging, encryption, and privacy controls before processing protected health information.
- Replace the demo fallback with an explicit offline/error state in any clinical environment, so generated static content cannot be mistaken for retrieved evidence.
- Add automated API, retrieval, schema, and end-to-end tests.
- Separate or expand prompts and structured input models for pulmonology, infectious disease, pharmacy, and other supported specialties.
- Implement clinical governance, human review, and appropriate regulatory/privacy assessment before deployment.
