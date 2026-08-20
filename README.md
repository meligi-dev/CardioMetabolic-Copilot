# Cardiometabolic Clinical Practice Guideline Copilot

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-green.svg)](https://www.python.org/)
[![React 19](https://img.shields.io/badge/React-19-blue.svg)](https://react.dev/)
[![Weaviate](https://img.shields.io/badge/Vector_DB-Weaviate_Cloud-red.svg)](https://weaviate.io/)

An evidence-grounded clinical decision-support platform for licensed healthcare professionals. The copilot transforms patient lab parameters and natural-language queries into verifiable pharmacotherapy recommendations grounded in official clinical practice guidelines (ADA 2024, ACC/AHA 2023, KDIGO 2023, GOLD/GINA 2024, IDSA 2024).

---

## 🌟 Key Features

* **Dual Clinical Workflows**:
  * **Patient Parameter Analyzer**: Accepts numerical labs (HbA1c, eGFR, UACR, LVEF, Blood Pressure) and comorbidities (ASCVD, Heart Failure, CKD) to output evidence-graded treatment plans.
  * **Clinical Guideline Q&A**: Answers free-text physician queries with direct guideline citations and evidence grades.
* **Zero-Hallucination & Anti-Grounding Engine**:
  * **Post-Processing Entity Verification**: Automatically cross-references query terms against retrieved guideline excerpts. If ungrounded or non-existent concepts (e.g. fabricated drug names) are detected, it issues a visual red warning alert and refrains from generating unverified recommendations.
  * **100% Traceable Citations**: Every drug recommendation requires exact Class of Recommendation (Class I, Class IIa, Class III) and Level of Evidence (Level A, Level B) with verifiable source snippets.
* **Active Inquiry Engine**:
  * Proactively identifies missing diagnostic biomarkers (e.g., missing UACR or LVEF) and generates targeted clinical follow-up questions explaining *why* the missing parameter affects therapy selection.
* **Organ Function Safety Thresholds**:
  * Enforces automatic renal dosing rules (e.g., Metformin discontinuation at eGFR < 30) and flags Class III contraindications (e.g., avoiding TZDs/NSAIDs in heart failure).

---

## 🏗️ Architecture

```text
React 19 + Vite Frontend
        │
        │ HTTP POST (/api/analyze-patient, /api/query)
        ▼
FastAPI Backend Engine
        │
        ├──► Weaviate Hybrid Search (BM25 + Vector Similarity, alpha=0.65)
        │       │
        │       └─► Retrieves Guideline Chunks + Parent Section Context
        │
        ├──► OpenAI-Compatible LLM Endpoint (e.g., Qwen 2.5 / OpenRouter)
        │
        └─► Post-Processing Sanitizer (Anti-Hallucination & Entity Check)
                │
                ▼
      Structured Clinical Analysis JSON
```

---

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* Node.js 18+ and npm
* A Weaviate Cloud instance & API key
* An OpenAI-compatible LLM endpoint API key (e.g., OpenRouter / Groq / OpenAI)

### 1. Environment Setup

Create a `.env` file in the root directory:

```env
WEAVIATE_URL=https://your-cluster-name.c0.eu-central-1.aws.weaviate.cloud
WEAVIATE_API_KEY=your-weaviate-api-key
LLM_API_KEY=your-llm-api-key
LLM_MODEL=qwen/qwen3.8-27b
LLM_BASE_URL=https://openrouter.ai/api/v1
```

### 2. Backend Installation & Run

```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```
The backend API will be available at `http://localhost:8000/api`.

### 3. Frontend Installation & Run

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Testing & Anti-Hallucination Verification

Run the automated anti-hallucination test suite:

```powershell
python test_hallucination_prevention.py
```

Run retrieval evaluation benchmarks:

```powershell
python eval/evaluate_benchmark.py
```

---

## 📚 Guideline Sources Included

| Source | Specialty / Content |
| :--- | :--- |
| **ADA 2024** | Glycemic targets, obesity/weight management, pharmacology, cardiovascular disease, neuropathy/retinopathy |
| **ACC/AHA/HFSA 2023** | Heart failure GDMT, hypertension management, dyslipidemia, ASCVD |
| **KDIGO 2023** | Chronic Kidney Disease (CKD) staging, eGFR thresholds, UACR microalbuminuria management |
| **GOLD & GINA 2024** | COPD Group A/B/E, Asthma SMART Track 1 protocols |
| **IDSA 2024** | Sepsis 1-hr bundle, community-acquired pneumonia, UTI treatment |

---

## ⚠️ Disclaimer

This application is an artificial intelligence decision-support tool intended **strictly for licensed healthcare professionals**. It is designed to assist and inform—not replace—clinical judgment, local institutional protocols, formal medication reconciliation, or specialist consultations.
