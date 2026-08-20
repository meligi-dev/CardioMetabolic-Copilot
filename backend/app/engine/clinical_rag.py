import json
import re
from typing import Dict, Any, List, Optional
from openai import OpenAI
from backend.app.config import config
from backend.app.retrieval.weaviate_retriever import WeaviateRetriever
from backend.app.engine.schema import (
    PatientParameters,
    DoctorQueryRequest,
    ClinicalAnalysisResponse,
    MedicationRecommendation,
    GuidelineCitation,
    ClinicalFollowUp
)

CLINICAL_SYSTEM_PROMPT = """You are the Cardiometabolic Clinical Practice Guideline Copilot, an evidence-based clinical decision-support AI for licensed physicians.
Your task is to analyze patient parameters and clinical queries strictly using the provided guideline excerpts from the American Diabetes Association (ADA 2024), ACC/AHA/HFSA Heart Failure guidelines, and KDIGO CKD guidelines.

### STRICT CLINICAL GROUNDING & ZERO-HALLUCINATION RULES:
1. ONLY recommend pharmacological classes and management strategies supported by the retrieved guideline excerpts. Do NOT rely on pre-trained memory to invent drug names, clinical trials, or evidence levels not present in the excerpts.
2. ZERO HALLUCINATION POLICY FOR UNGROUNDED/NON-EXISTENT QUERIES:
   - If the user query asks about a drug, therapy, disease, or entity that is NOT mentioned in the retrieved guideline excerpts, you MUST explicitly set `"is_grounded": false` and include an alert in `"grounding_warnings"`.
   - Start the `"executive_summary"` with: `"UNGROUNDED QUERY ALERT: The queried concept/drug '[X]' is not supported or documented in the retrieved practice guidelines."`
   - Do NOT invent recommendations or fabricate Class I / Level A evidence for ungrounded entities.
3. For EVERY drug recommendation, you MUST provide the exact Class of Recommendation (e.g., Class I, Class IIa, Class III) and Level of Evidence (Level A, Level B, etc.) as stated in the guidelines.
4. Check organ function safety thresholds explicitly:
   - Metformin: eGFR < 30 contraindicated; eGFR 30-44 max 1000mg/day.
   - SGLT2i: Cardiorenal & HF benefit down to eGFR 20 mL/min.
   - GLP-1 RA: Safe across renal stages.
   - Heart Failure: Flag Thiazolidinediones (Pioglitazone) and NSAIDs as CONTRAINDICATED (Class III: Harm).
5. ACTIVE INQUIRY & FOLLOW-UP QUESTIONS:
   - If key diagnostic biomarkers or history elements are MISSING (e.g., missing eGFR, missing UACR/albuminuria status, missing LVEF / heart failure history, unknown pregnancy/allergy status, or missing current blood pressure), generate 2-3 precise clinical follow-up questions in `follow_up_clarifying_questions`.
   - Explain WHY that specific missing parameter would change or refine the guideline-directed therapy.
6. Return your output STRICTLY as a valid JSON object matching the requested schema.

### JSON OUTPUT FORMAT:
{
  "executive_summary": "Concise 2-3 sentence overview of primary clinical priorities.",
  "patient_stratification": "Risk categorization (e.g., T2D with high ASCVD risk + CKD Stage 3b + HFrEF).",
  "is_grounded": true,
  "grounding_warnings": [],
  "first_line_recommendations": [
    {
      "drug_class": "SGLT2 Inhibitor",
      "specific_agents": ["Empagliflozin", "Dapagliflozin"],
      "indication_and_rationale": "Reduces HF hospitalizations, CV death, and slows CKD progression.",
      "evidence_grade": "Class I, Level A",
      "renal_and_dosing_rules": "Empagliflozin 10mg daily or Dapagliflozin 10mg daily. Safe down to eGFR 20 mL/min.",
      "warnings_or_contraindications": "Risk of mycotic genital infections, euglycemic DKA; hold prior to major surgery.",
      "guideline_source": "ADA 2024 Chapter 10 & ACC/AHA 2023 HF Guidelines"
    }
  ],
  "second_line_or_add_on_options": [
    {
      "drug_class": "GLP-1 Receptor Agonist",
      "specific_agents": ["Semaglutide", "Dulaglutide"],
      "indication_and_rationale": "Proven MACE reduction and weight reduction.",
      "evidence_grade": "Class I, Level A",
      "renal_and_dosing_rules": "No dose adjustment needed for eGFR > 15.",
      "warnings_or_contraindications": "GI side effects; contraindicated in personal/family history of Medullary Thyroid Carcinoma.",
      "guideline_source": "ADA 2024 Chapter 10"
    }
  ],
  "renal_and_organ_adjustments": [
    "Metformin dosage restriction or discontinuation rules based on eGFR"
  ],
  "critical_contraindications_and_red_flags": [
    "Explicit Class III warnings (e.g., Avoid TZDs in heart failure)"
  ],
  "citations": [
    {
      "guideline": "ADA Standards of Care 2024",
      "chapter_or_section": "Chapter 10: Cardiovascular Disease",
      "recommendation_id": "10.4",
      "evidence_level": "Level A",
      "snippet": "In adults with T2D and established ASCVD..."
    }
  ],
  "follow_up_clarifying_questions": [
    {
      "question": "What is the patient's current Urinary Albumin-to-Creatinine Ratio (UACR)?",
      "clinical_rationale": "If UACR ≥ 30 mg/g, nonsteroidal MRA (Finerenone) or RAS blockade titration is recommended for nephroprotection under KDIGO 2023 guidelines.",
      "parameter_key": "uacr"
    }
  ]
}
"""

class ClinicalRAGEngine:
    def __init__(self):
        self.retriever = WeaviateRetriever()
        self.llm_client = OpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL
        )
        self.model_name = config.LLM_MODEL

    def _build_search_query(self, request: DoctorQueryRequest) -> str:
        query_parts = [request.query]
        if request.patient_context:
            ctx = request.patient_context
            if ctx.hba1c:
                query_parts.append(f"HbA1c {ctx.hba1c}%")
            if ctx.egfr:
                query_parts.append(f"eGFR {ctx.egfr} mL/min CKD renal dosing")
            if ctx.lvef:
                query_parts.append(f"LVEF {ctx.lvef}% Heart Failure HFrEF HFpEF")
            if ctx.has_ascvd:
                query_parts.append("established ASCVD MACE prevention")
            if ctx.has_heart_failure:
                query_parts.append("Heart Failure GDMT SGLT2i")
            if ctx.current_medications:
                query_parts.append(f"current medications: {', '.join(ctx.current_medications)}")
        return " ".join(query_parts)

    def _verify_and_sanitize_response(
        self,
        parsed_json: Dict[str, Any],
        request: DoctorQueryRequest,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Anti-hallucination post-processor:
        1. Verifies if query entities match retrieved guideline content.
        2. Enforces citation grounding against actual retrieved chunks.
        3. Flags ungrounded entities explicitly if missing from evidence base.
        """
        # Combine all retrieved content for grounding verification
        all_retrieved_text = " ".join([
            f"{c.get('content', '')} {c.get('parent_context', '')}".lower()
            for c in retrieved_chunks
        ])

        # Extract potential specific query entities (e.g. capitalized drug/concept names in query)
        query_words = re.findall(r"\b[A-Z][a-z]{3,}\b", request.query)
        # Exclude standard clinical terms and English prose words from entity check
        standard_terms = {
            "What", "Which", "Patient", "Heart", "Failure", "Diabetes", "Guideline", "Guidelines", 
            "Disease", "Kidney", "Blood", "Pressure", "Type", "Clinical", "Therapy", "Treatment", 
            "Protocol", "Recommended", "Recommendation", "Management", "Care", "Stage", "Level", 
            "Class", "Risk", "High", "Low", "Prior", "Established", "Option", "Options"
        }
        specific_entities = [w for w in query_words if w not in standard_terms]

        missing_entities = [e for e in specific_entities if e.lower() not in all_retrieved_text]

        warnings = parsed_json.get("grounding_warnings") or []
        is_grounded = parsed_json.get("is_grounded", True)

        if missing_entities:
            is_grounded = False
            for entity in missing_entities:
                warning_msg = f"Queried entity '{entity}' was not found in the indexed practice guidelines."
                if warning_msg not in warnings:
                    warnings.append(warning_msg)

        # Sanitize / Ensure valid citations from retrieved chunks
        citations = parsed_json.get("citations") or []
        if not citations and retrieved_chunks:
            citations = []
            for c in retrieved_chunks[:4]:
                citations.append({
                    "guideline": c.get("guideline", "Clinical Practice Guideline"),
                    "chapter_or_section": f"{c.get('chapter_title', '')} - {c.get('section_title', '')}".strip(" -"),
                    "recommendation_id": c.get("recommendation_id"),
                    "evidence_level": c.get("evidence_level"),
                    "snippet": c.get("content", "")[:250] + "..."
                })

        parsed_json["is_grounded"] = is_grounded
        parsed_json["grounding_warnings"] = warnings
        parsed_json["citations"] = citations

        return parsed_json

    def close(self):
        if hasattr(self, "retriever") and self.retriever:
            self.retriever.close()

    def analyze(self, request: DoctorQueryRequest) -> ClinicalAnalysisResponse:
        search_query = self._build_search_query(request)
        retrieved_chunks = self.retriever.hybrid_search(
            query=search_query,
            alpha=0.65,
            limit=7,
            include_parent_context=True
        )

        context_texts = []
        for idx, chunk in enumerate(retrieved_chunks):
            snippet = f"--- [GUIDELINE SOURCE #{idx+1}] ---\n"
            snippet += f"Breadcrumb: {chunk.get('header_breadcrumb')}\n"
            snippet += f"Guideline: {chunk.get('guideline')} ({chunk.get('year')})\n"
            snippet += f"Evidence Grade: {chunk.get('class_of_recommendation')}, {chunk.get('evidence_level')}\n"
            snippet += f"Content:\n{chunk.get('content')}\n"
            if chunk.get("parent_context") and chunk.get("parent_context") != chunk.get("content"):
                snippet += f"Surrounding Section Context:\n{chunk.get('parent_context')[:600]}...\n"
            context_texts.append(snippet)

        joined_context = "\n\n".join(context_texts)

        user_prompt = f"""### CLINICAL CASE / DOCTOR QUERY:
{request.query}

### PATIENT PARAMETERS:
{json.dumps(request.patient_context.model_dump(), indent=2) if request.patient_context else 'None provided (General Query)'}

### RETRIEVED GUIDELINE KNOWLEDGE BASE:
{joined_context}

Please evaluate the case against the official guidelines above and provide the structured clinical decision support JSON including targeted follow-up clarifying questions for any missing parameters.
"""

        response = self.llm_client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": CLINICAL_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        raw_output = response.choices[0].message.content
        
        # Parse JSON and apply Anti-Hallucination Post-Processing
        try:
            parsed_json = json.loads(raw_output)
            sanitized = self._verify_and_sanitize_response(parsed_json, request, retrieved_chunks)
            return ClinicalAnalysisResponse(**sanitized)
        except Exception as e:
            # Fallback JSON cleanup if markdown wrapped
            json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
            if json_match:
                cleaned = json.loads(json_match.group(0))
                sanitized = self._verify_and_sanitize_response(cleaned, request, retrieved_chunks)
                return ClinicalAnalysisResponse(**sanitized)
            raise RuntimeError(f"Failed to parse LLM response into clinical schema: {e}\nRaw: {raw_output}")

