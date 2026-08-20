from fastapi import APIRouter, HTTPException
from backend.app.engine.schema import (
    DoctorQueryRequest,
    ClinicalAnalysisResponse,
    PatientParameters
)
from backend.app.engine.clinical_rag import ClinicalRAGEngine

router = APIRouter(prefix="/api", tags=["Clinical Decision Support"])

# Lazy initialize engine
_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = ClinicalRAGEngine()
    return _engine

@router.post("/analyze-patient", response_model=ClinicalAnalysisResponse)
async def analyze_patient(patient: PatientParameters):
    """
    Analyzes numerical and diagnostic patient parameters against guidelines.
    """
    try:
        engine = get_engine()
        # Formulate query based on parameters
        conditions = []
        if patient.hba1c and patient.hba1c > 7.0:
            conditions.append(f"Uncontrolled T2D (HbA1c {patient.hba1c}%)")
        if patient.egfr and patient.egfr < 60:
            conditions.append(f"CKD (eGFR {patient.egfr})")
        if patient.has_ascvd:
            conditions.append("Established ASCVD / Prior MI")
        if patient.has_heart_failure or (patient.lvef and patient.lvef <= 40):
            conditions.append(f"Heart Failure (LVEF {patient.lvef or 'Reduced'}%)")

        query_summary = f"Guideline-directed medical therapy and drug safety analysis for patient with: {', '.join(conditions) if conditions else 'Cardiometabolic risk evaluation'}"
        if patient.clinical_notes:
            query_summary += f". Notes: {patient.clinical_notes}"

        request = DoctorQueryRequest(
            query=query_summary,
            patient_context=patient
        )
        return engine.analyze(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=ClinicalAnalysisResponse)
async def query_guidelines(request: DoctorQueryRequest):
    """
    Handles natural language doctor questions with optional patient context.
    """
    try:
        engine = get_engine()
        return engine.analyze(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "Cardiometabolic Clinical Guideline Copilot"}
