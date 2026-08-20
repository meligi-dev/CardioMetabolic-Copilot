import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.app.engine.schema import DoctorQueryRequest, PatientParameters
from backend.app.engine.clinical_rag import ClinicalRAGEngine

def test_three_clinical_cases():
    engine = ClinicalRAGEngine()

    # --- CASE 1: Heart Problem (Heart Failure / HFrEF) ---
    print("=" * 80)
    print("CASE 1: Heart Problem (Heart Failure / HFrEF)")
    print("=" * 80)
    hf_query = "What is the guideline-directed therapy for a patient with HFrEF (LVEF 30%) and Type 2 Diabetes?"
    hf_req = DoctorQueryRequest(
        query=hf_query,
        patient_context=PatientParameters(lvef=30, has_heart_failure=True, hba1c=8.2)
    )
    
    hf_chunks = [
        {
            "guideline": "ACC/AHA/HFSA Heart Failure Guideline 2023",
            "chapter_title": "Chapter 1: GDMT 4-Pillar Pharmacotherapy",
            "section_title": "1.2 HFrEF Management",
            "content": "SGLT2 inhibitors (Empagliflozin or Dapagliflozin) are Class I, Level A recommended in HFrEF to reduce CV death and HF hospitalizations.",
            "parent_context": "ACC/AHA 2023 Heart Failure Guidelines: Guideline-Directed Medical Therapy for HFrEF.",
            "recommendation_id": "Rec 1.2",
            "evidence_level": "Level A",
            "class_of_recommendation": "Class I"
        }
    ]
    
    hf_mock_json = {
        "executive_summary": "In HFrEF (LVEF 30%), GDMT requires initiation of SGLT2i alongside foundational HF therapy.",
        "patient_stratification": "HFrEF (LVEF 30%) + T2D",
        "is_grounded": True,
        "grounding_warnings": [],
        "first_line_recommendations": [
            {
                "drug_class": "SGLT2 Inhibitor",
                "specific_agents": ["Empagliflozin 10mg daily", "Dapagliflozin 10mg daily"],
                "indication_and_rationale": "Class I recommendation for mortality and HF hospitalization reduction.",
                "evidence_grade": "Class I, Level A",
                "renal_and_dosing_rules": "Safe down to eGFR 20 mL/min.",
                "warnings_or_contraindications": "Hold prior to major surgery; monitor volume status.",
                "guideline_source": "ACC/AHA 2023 HF Guidelines"
            }
        ],
        "second_line_or_add_on_options": [],
        "renal_and_organ_adjustments": [],
        "critical_contraindications_and_red_flags": ["Avoid Thiazolidinediones (Pioglitazone) in Heart Failure (Class III: Harm)."],
        "citations": [],
        "follow_up_clarifying_questions": []
    }
    
    res_hf = engine._verify_and_sanitize_response(hf_mock_json, hf_req, hf_chunks)
    print(f"Query: {hf_query}")
    print(f"Summary: {res_hf['executive_summary']}")
    print(f"Is Grounded: {res_hf['is_grounded']}")
    print(f"First-Line Rec: {res_hf['first_line_recommendations'][0]['drug_class']} ({res_hf['first_line_recommendations'][0]['evidence_grade']})")
    assert res_hf['is_grounded'] == True

    # --- CASE 2: CAD Problem (Coronary Artery Disease / ASCVD) ---
    print("\n" + "=" * 80)
    print("CASE 2: CAD Problem (Coronary Artery Disease / ASCVD)")
    print("=" * 80)
    cad_query = "What is the recommended therapy for a patient with established CAD, prior MI, and uncontrolled HbA1c 8.8%?"
    cad_req = DoctorQueryRequest(
        query=cad_query,
        patient_context=PatientParameters(has_ascvd=True, hba1c=8.8)
    )
    
    cad_chunks = [
        {
            "guideline": "ADA Standards of Care 2024",
            "chapter_title": "Chapter 10: Cardiovascular Disease",
            "section_title": "10.4 ASCVD Risk Reduction",
            "content": "In T2D with established ASCVD or CAD, GLP-1 RA or SGLT2i with proven MACE benefit is Class I Level A recommended.",
            "parent_context": "ADA 2024 Chapter 10: Cardiovascular Disease and Risk Management.",
            "recommendation_id": "Rec 10.4",
            "evidence_level": "Level A",
            "class_of_recommendation": "Class I"
        }
    ]
    
    cad_mock_json = {
        "executive_summary": "In T2D with established CAD and prior MI, GLP-1 RA or SGLT2i is Class I recommended for MACE reduction.",
        "patient_stratification": "Established CAD / Prior MI + T2D",
        "is_grounded": True,
        "grounding_warnings": [],
        "first_line_recommendations": [
            {
                "drug_class": "GLP-1 Receptor Agonist",
                "specific_agents": ["Semaglutide", "Dulaglutide"],
                "indication_and_rationale": "Proven MACE reduction in established CAD.",
                "evidence_grade": "Class I, Level A",
                "renal_and_dosing_rules": "No dose adjustment required.",
                "warnings_or_contraindications": "GI side effects; contraindicated in MTC.",
                "guideline_source": "ADA 2024 Chapter 10"
            }
        ],
        "second_line_or_add_on_options": [],
        "renal_and_organ_adjustments": ["Maintain high-intensity statin therapy for secondary ASCVD prevention."],
        "critical_contraindications_and_red_flags": [],
        "citations": [],
        "follow_up_clarifying_questions": []
    }
    
    res_cad = engine._verify_and_sanitize_response(cad_mock_json, cad_req, cad_chunks)
    print(f"Query: {cad_query}")
    print(f"Summary: {res_cad['executive_summary']}")
    print(f"Is Grounded: {res_cad['is_grounded']}")
    print(f"First-Line Rec: {res_cad['first_line_recommendations'][0]['drug_class']} ({res_cad['first_line_recommendations'][0]['evidence_grade']})")
    assert res_cad['is_grounded'] == True

    # --- CASE 3: Refusal Case (Ungrounded / Non-Existent Entity / Out-of-Scope Query) ---
    print("\n" + "=" * 80)
    print("CASE 3: Refusal Case (Ungrounded / Non-Existent Entity Query)")
    print("=" * 80)
    refusal_query = "What is the initial dosage protocol for Xylopharyngol in treating anterior cervical discectomy?"
    refusal_req = DoctorQueryRequest(query=refusal_query)
    
    refusal_mock_json = {
        "executive_summary": "UNGROUNDED QUERY ALERT: The requested query terms are not present in practice guidelines.",
        "patient_stratification": "Ungrounded Query",
        "is_grounded": False,
        "grounding_warnings": ["Queried entity 'Xylopharyngol' was not found in the indexed practice guidelines."],
        "first_line_recommendations": [],
        "second_line_or_add_on_options": [],
        "renal_and_organ_adjustments": [],
        "critical_contraindications_and_red_flags": ["Refused ungrounded generation for unverified drug/procedure."],
        "citations": [],
        "follow_up_clarifying_questions": []
    }
    
    res_refusal = engine._verify_and_sanitize_response(refusal_mock_json, refusal_req, cad_chunks)
    print(f"Query: {refusal_query}")
    print(f"Summary: {res_refusal['executive_summary']}")
    print(f"Is Grounded: {res_refusal['is_grounded']}")
    print(f"Grounding Warnings: {res_refusal['grounding_warnings']}")
    assert res_refusal['is_grounded'] == False
    assert len(res_refusal['grounding_warnings']) > 0

    engine.close()
    print("\nALL 3 TEST CASES (HEART PROBLEM, CAD PROBLEM, REFUSAL CASE) PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_three_clinical_cases()
