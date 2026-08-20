from typing import List, Optional
from pydantic import BaseModel, Field

class PatientParameters(BaseModel):
    age: Optional[int] = Field(None, description="Patient age in years")
    gender: Optional[str] = Field(None, description="Male / Female / Other")
    hba1c: Optional[float] = Field(None, description="HbA1c level in percentage, e.g. 8.5")
    egfr: Optional[float] = Field(None, description="eGFR in mL/min/1.73m2, e.g. 35")
    uacr: Optional[float] = Field(None, description="Urine Albumin-to-Creatinine Ratio in mg/g, e.g. 150")
    blood_pressure: Optional[str] = Field(None, description="Blood pressure, e.g. '145/88'")
    lvef: Optional[float] = Field(None, description="Left Ventricular Ejection Fraction in percentage, e.g. 35")
    has_ascvd: Optional[bool] = Field(False, description="Prior MI, Stroke, Stent, CAD, PAD")
    has_heart_failure: Optional[bool] = Field(False, description="Heart Failure diagnosed (HFrEF / HFpEF)")
    has_ckd: Optional[bool] = Field(False, description="Chronic Kidney Disease")
    current_medications: Optional[List[str]] = Field(default_factory=list, description="Currently prescribed meds")
    allergies_or_intolerances: Optional[List[str]] = Field(default_factory=list, description="Known drug allergies")
    clinical_notes: Optional[str] = Field(None, description="Additional physician notes or case description")

class DoctorQueryRequest(BaseModel):
    query: str
    patient_context: Optional[PatientParameters] = None

class GuidelineCitation(BaseModel):
    guideline: str
    chapter_or_section: str
    recommendation_id: Optional[str] = None
    evidence_level: Optional[str] = None
    snippet: str

class MedicationRecommendation(BaseModel):
    drug_class: str
    specific_agents: List[str]
    indication_and_rationale: str
    evidence_grade: str  # e.g. "Class I, Level A"
    renal_and_dosing_rules: str
    warnings_or_contraindications: str
    guideline_source: str

class ClinicalFollowUp(BaseModel):
    question: str = Field(..., description="The clinical clarifying question")
    clinical_rationale: str = Field(..., description="Why this missing information is crucial for guideline compliance")
    parameter_key: Optional[str] = Field(None, description="Target field e.g. 'egfr', 'uacr', 'lvef', 'ascvd'")

class ClinicalAnalysisResponse(BaseModel):
    executive_summary: str
    patient_stratification: str
    first_line_recommendations: List[MedicationRecommendation]
    second_line_or_add_on_options: List[MedicationRecommendation]
    renal_and_organ_adjustments: List[str]
    critical_contraindications_and_red_flags: List[str]
    citations: List[GuidelineCitation]
    follow_up_clarifying_questions: List[ClinicalFollowUp] = Field(
        default_factory=list,
        description="Targeted follow-up questions to gather missing clinical biomarkers or history"
    )
    is_grounded: bool = Field(
        default=True,
        description="True if recommendations are verified against retrieved clinical guidelines; False if ungrounded query terms exist"
    )
    grounding_warnings: List[str] = Field(
        default_factory=list,
        description="Explicit warnings when queries or entities are ungrounded or unsupported by retrieved guideline excerpts"
    )
