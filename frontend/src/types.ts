export interface PatientParameters {
  age?: number;
  gender?: string;
  hba1c?: number;
  egfr?: number;
  uacr?: number;
  blood_pressure?: string;
  lvef?: number;
  has_ascvd?: boolean;
  has_heart_failure?: boolean;
  has_ckd?: boolean;
  current_medications?: string[];
  allergies_or_intolerances?: string[];
  clinical_notes?: string;
}

export interface GuidelineCitation {
  guideline: string;
  chapter_or_section: string;
  recommendation_id?: string;
  evidence_level?: string;
  snippet: string;
}

export interface MedicationRecommendation {
  drug_class: string;
  specific_agents: string[];
  indication_and_rationale: string;
  evidence_grade: string;
  renal_and_dosing_rules: string;
  warnings_or_contraindications: string;
  guideline_source: string;
}

export interface ClinicalFollowUp {
  question: string;
  clinical_rationale: string;
  parameter_key?: string;
}

export interface ClinicalAnalysisResponse {
  executive_summary: string;
  patient_stratification: string;
  first_line_recommendations: MedicationRecommendation[];
  second_line_or_add_on_options: MedicationRecommendation[];
  renal_and_organ_adjustments: string[];
  critical_contraindications_and_red_flags: string[];
  citations: GuidelineCitation[];
  follow_up_clarifying_questions?: ClinicalFollowUp[];
  is_grounded?: boolean;
  grounding_warnings?: string[];
}
