import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app.engine.schema import DoctorQueryRequest, PatientParameters, ClinicalAnalysisResponse
from backend.app.engine.clinical_rag import ClinicalRAGEngine

def test_unit_sanitizer_logic():
    print("Testing Anti-Hallucination Post-Processor Unit Logic...")
    engine = ClinicalRAGEngine()

    mock_retrieved_chunks = [
        {
            "guideline": "ADA Standards of Care 2024",
            "chapter_title": "Chapter 10: Cardiovascular Disease",
            "section_title": "10.4 Pharmacotherapy",
            "content": "In patients with T2D and eGFR >= 20 mL/min, Empagliflozin or Dapagliflozin is recommended for cardiorenal protection.",
            "parent_context": "Chapter 10: Cardiovascular Disease and Risk Management in Diabetes.",
            "recommendation_id": "10.4",
            "evidence_level": "Level A"
        }
    ]

    # Test 1: Query with non-existent drug 'Xylopharyngol'
    fake_req = DoctorQueryRequest(query="What is the dosage for Xylopharyngol in CKD?")
    mock_raw_parsed = {
        "executive_summary": "Xylopharyngol is recommended for CKD.",
        "patient_stratification": "CKD Stage 3",
        "first_line_recommendations": [],
        "second_line_or_add_on_options": [],
        "renal_and_organ_adjustments": [],
        "critical_contraindications_and_red_flags": [],
        "citations": [],
        "follow_up_clarifying_questions": []
    }

    sanitized_fake = engine._verify_and_sanitize_response(mock_raw_parsed, fake_req, mock_retrieved_chunks)
    print(f"[Unit Test] Fake Drug Query -> is_grounded: {sanitized_fake['is_grounded']}, warnings: {sanitized_fake['grounding_warnings']}")
    assert sanitized_fake["is_grounded"] == False, "Post-processor must set is_grounded=False when query entity is missing from retrieved text"
    assert any("Xylopharyngol" in w for w in sanitized_fake["grounding_warnings"]), "Warning must mention ungrounded entity name"

    # Test 2: Valid drug query 'Empagliflozin'
    valid_req = DoctorQueryRequest(query="What is the evidence for Empagliflozin?")
    mock_valid_parsed = {
        "executive_summary": "Empagliflozin reduces cardiorenal risk.",
        "patient_stratification": "T2D with CKD",
        "is_grounded": True,
        "grounding_warnings": [],
        "first_line_recommendations": [],
        "second_line_or_add_on_options": [],
        "renal_and_organ_adjustments": [],
        "critical_contraindications_and_red_flags": [],
        "citations": [],
        "follow_up_clarifying_questions": []
    }
    sanitized_valid = engine._verify_and_sanitize_response(mock_valid_parsed, valid_req, mock_retrieved_chunks)
    print(f"[Unit Test] Valid Drug Query -> is_grounded: {sanitized_valid['is_grounded']}, citations attached: {len(sanitized_valid['citations'])}")
    assert sanitized_valid["is_grounded"] == True, "Valid query with matching retrieved text must remain grounded"
    assert len(sanitized_valid["citations"]) > 0, "Citations must be auto-populated from retrieved chunks if omitted by model"

    engine.close()
    print("ALL UNIT TESTS FOR POST-PROCESSOR SANITIZER PASSED SUCCESSFULLY!\n")

def test_live_engine_if_available():
    engine = None
    try:
        print("Testing Live Engine Endpoint...")
        engine = ClinicalRAGEngine()
        req = DoctorQueryRequest(
            query="What is the guideline evidence for Empagliflozin in eGFR 35?",
            patient_context=PatientParameters(egfr=35)
        )
        res = engine.analyze(req)
        print(f"[Live Test] Executive Summary: {res.executive_summary[:100]}...")
        print(f"[Live Test] Grounded: {res.is_grounded}")
    except Exception as e:
        print(f"[Live Test Info] Live endpoint test skipped or failed with credentials: {e}")
    finally:
        if engine:
            engine.close()

if __name__ == "__main__":
    test_unit_sanitizer_logic()
    test_live_engine_if_available()
