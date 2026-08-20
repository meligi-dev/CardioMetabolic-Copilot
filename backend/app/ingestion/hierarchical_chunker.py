import os
import re
from typing import List, Dict, Any

class HierarchicalChunker:
    """
    Parses hospital guidelines and global drug formularies into atomic child recommendation chunks 
    and parent section blocks, embedding hierarchy breadcrumbs.
    """
    def __init__(self):
        # Regex patterns for clinical recommendation & drug bullet structure
        self.re_rec = re.compile(r"^\*\s+\*\*([^\*]+)\*\*:?\s*(.+?)(?=\n\*\s+\*\*|\n###|\n##|\n#|\Z)", re.DOTALL | re.MULTILINE)
        self.re_loe = re.compile(r"\((Class\s+[I|II|III|IVa-c]+,\s*)?(Level\s+[A-C1-2]+[A-B]?|Class\s+[I|II|III|IVa-c]+[^)]*|Black\s+Box\s+Warning[^)]*)\)", re.IGNORECASE)

    def parse_file(self, filepath: str) -> List[Dict[str, Any]]:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()

        filename = os.path.basename(filepath).lower()
        chunks = []

        # Determine guideline source name
        if "ada" in filename:
            guideline_source = "ADA Standards of Care 2024"
        elif "acc" in filename or "aha" in filename:
            guideline_source = "ACC/AHA Clinical Practice Guideline"
        elif "kdigo" in filename:
            guideline_source = "KDIGO 2023 Guideline"
        elif "gold" in filename or "gina" in filename:
            guideline_source = "GOLD & GINA 2024 Respiratory Guideline"
        elif "idsa" in filename:
            guideline_source = "IDSA & Sepsis Campaign 2024"
        elif "drug" in filename or "formulary" in filename:
            guideline_source = "WHO & FDA Global Drug Formulary"
        else:
            guideline_source = "Clinical Hospital Guideline"

        # Split by sections (###)
        sections = re.split(r"(?=^###\s+)", raw_text, flags=re.MULTILINE)
        
        chapter_match = re.search(r"^##\s+(.+)$", raw_text, re.MULTILINE)
        chapter_title = chapter_match.group(1).strip() if chapter_match else "Hospital Protocol"
        
        ch_num_match = re.search(r"Chapter\s+(\d+)", chapter_title, re.IGNORECASE)
        chapter_num = int(ch_num_match.group(1)) if ch_num_match else 1

        for sec_idx, sec_text in enumerate(sections):
            sec_header_match = re.search(r"^###\s+(.+)$", sec_text, re.MULTILINE)
            sec_title = sec_header_match.group(1).strip() if sec_header_match else f"Section {sec_idx + 1}"

            parent_id = f"{guideline_source[:4].lower()}_ch{chapter_num}_sec{sec_idx}"
            parent_content = sec_text.strip()

            # 1. Check if section has tables
            if "| --- |" in sec_text or "|:---" in sec_text:
                table_lines = [line for line in sec_text.split("\n") if "|" in line]
                table_content = "\n".join(table_lines)
                
                header_breadcrumb = f"[{guideline_source}] > [{chapter_title}] > [{sec_title}] (Clinical Reference Table)"
                chunk_payload = {
                    "content": f"{header_breadcrumb}\n\n{table_content}",
                    "header_breadcrumb": header_breadcrumb,
                    "guideline": guideline_source,
                    "year": 2024,
                    "chapter_num": chapter_num,
                    "chapter_title": chapter_title,
                    "section_title": sec_title,
                    "recommendation_id": "Table",
                    "evidence_level": "Guideline Standard",
                    "class_of_recommendation": "Class I / Standard",
                    "target_conditions": ["Cardiometabolic", "Hospital Care"],
                    "parent_id": parent_id,
                    "parent_content": parent_content,
                    "is_table": True
                }
                chunks.append(chunk_payload)

            # 2. Extract atomic recommendations and drug items
            rec_matches = self.re_rec.findall(sec_text)
            if rec_matches:
                for rec_id_raw, rec_body in rec_matches:
                    rec_id = rec_id_raw.strip()
                    clean_body = re.sub(r"\s+", " ", rec_body).strip()
                    
                    # Extract LOE / Class
                    loe_match = self.re_loe.search(clean_body)
                    evidence_level = loe_match.group(2) if loe_match else "Guideline Standard"
                    class_of_rec = loe_match.group(1).replace(",", "").strip() if loe_match and loe_match.group(1) else "Class I (Recommended)"

                    # Identify target conditions
                    target_conditions = []
                    lower_body = clean_body.lower() + " " + rec_id.lower()
                    if "ascvd" in lower_body or "mace" in lower_body or "coronary" in lower_body or "clopidogrel" in lower_body:
                        target_conditions.append("Cardiology / ASCVD")
                    if "heart failure" in lower_body or "hfref" in lower_body or "hfpef" in lower_body:
                        target_conditions.append("Heart Failure")
                    if "ckd" in lower_body or "egfr" in lower_body or "kidney" in lower_body:
                        target_conditions.append("Nephrology / CKD")
                    if "diabetes" in lower_body or "hba1c" in lower_body or "glucose" in lower_body:
                        target_conditions.append("Endocrinology / Diabetes")
                    if "copd" in lower_body or "asthma" in lower_body or "pulmonology" in lower_body:
                        target_conditions.append("Pulmonology")
                    if "sepsis" in lower_body or "pneumonia" in lower_body or "antibiotic" in lower_body:
                        target_conditions.append("Infectious Disease")
                    if not target_conditions:
                        target_conditions = ["General Medicine"]

                    header_breadcrumb = f"[{guideline_source}] > [{chapter_title}] > [{sec_title}] > [{rec_id}]"
                    
                    chunk_payload = {
                        "content": f"{header_breadcrumb}\n\n**{rec_id}**: {clean_body}",
                        "header_breadcrumb": header_breadcrumb,
                        "guideline": guideline_source,
                        "year": 2024,
                        "chapter_num": chapter_num,
                        "chapter_title": chapter_title,
                        "section_title": sec_title,
                        "recommendation_id": rec_id,
                        "evidence_level": evidence_level,
                        "class_of_recommendation": class_of_rec,
                        "target_conditions": target_conditions,
                        "parent_id": parent_id,
                        "parent_content": parent_content,
                        "is_table": False
                    }
                    chunks.append(chunk_payload)
            else:
                paragraphs = [p.strip() for p in sec_text.split("\n\n") if p.strip() and not p.startswith("###")]
                for p_idx, p_text in enumerate(paragraphs):
                    if len(p_text) < 40 or "|" in p_text:
                        continue
                    header_breadcrumb = f"[{guideline_source}] > [{chapter_title}] > [{sec_title}]"
                    chunk_payload = {
                        "content": f"{header_breadcrumb}\n\n{p_text}",
                        "header_breadcrumb": header_breadcrumb,
                        "guideline": guideline_source,
                        "year": 2024,
                        "chapter_num": chapter_num,
                        "chapter_title": chapter_title,
                        "section_title": sec_title,
                        "recommendation_id": f"{sec_title[:15]}-p{p_idx+1}",
                        "evidence_level": "Guideline Text",
                        "class_of_recommendation": "Standard",
                        "target_conditions": ["General Medicine"],
                        "parent_id": parent_id,
                        "parent_content": parent_content,
                        "is_table": False
                    }
                    chunks.append(chunk_payload)

        return chunks
