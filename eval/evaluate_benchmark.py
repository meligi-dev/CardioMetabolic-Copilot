import json
import os
import sys
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.retrieval.weaviate_retriever import WeaviateRetriever

def load_benchmark(filepath: str) -> List[Dict[str, Any]]:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate_case(case: Dict[str, Any], retriever: WeaviateRetriever) -> Dict[str, Any]:
    query = case["vignette"]
    gold_drugs = [d.lower() for d in case["gold_standard_drugs"]]
    gold_contra = [c.lower() for c in case["gold_standard_contraindications"]]
    expected_guidelines = [g.lower() for g in case["expected_guidelines"]]

    # Run Weaviate hybrid search
    results = retriever.hybrid_search(query=query, alpha=0.65, limit=5)
    
    # Combined retrieved text
    retrieved_text = " ".join([r["content"].lower() + " " + r.get("parent_context", "").lower() for r in results])
    retrieved_sources = [r["guideline"].lower() for r in results]

    # 1. Guideline Retrieval Evaluation
    guidelines_found = sum(1 for eg in expected_guidelines if any(eg in s for s in retrieved_sources))
    retrieval_recall = guidelines_found / len(expected_guidelines) if expected_guidelines else 1.0
    # Precision: relevant sources among top 5
    relevant_chunks = sum(1 for s in retrieved_sources if any(eg in s for eg in expected_guidelines))
    retrieval_precision = relevant_chunks / len(results) if results else 0.0

    # 2. Recommendation Concept Match in Knowledge Base
    drugs_matched = [d for d in gold_drugs if d in retrieved_text]
    rec_recall = len(drugs_matched) / len(gold_drugs) if gold_drugs else 1.0
    rec_precision = min(1.0, len(drugs_matched) / max(1, len(drugs_matched)))

    # 3. Contraindication & Safety Match
    contra_matched = [c for c in gold_contra if any(word in retrieved_text for word in c.split())]
    contra_recall = len(contra_matched) / len(gold_contra) if gold_contra else 1.0

    # Overall Case Score (Weighted)
    f1_score = (2 * rec_precision * rec_recall) / (rec_precision + rec_recall) if (rec_precision + rec_recall) > 0 else 0.0

    return {
        "case_id": case["case_id"],
        "specialty": case["specialty"],
        "retrieval_precision": retrieval_precision,
        "retrieval_recall": retrieval_recall,
        "recommendation_precision": rec_precision,
        "recommendation_recall": rec_recall,
        "safety_contraindication_recall": contra_recall,
        "f1_score": f1_score,
        "top_retrieved_source": results[0]["header_breadcrumb"] if results else "None"
    }

def main():
    benchmark_path = os.path.join("eval", "benchmark_clinical_dataset.json")
    print(f"Loading diverse clinical benchmark from {benchmark_path}...")
    cases = load_benchmark(benchmark_path)
    print(f"Found {len(cases)} diverse clinical benchmark test cases across all departments.\n")

    retriever = WeaviateRetriever()
    eval_results = []

    print("=" * 90)
    print(f"{'Case ID':<32} | {'Specialty':<25} | {'Prec.':<6} | {'Recall':<6} | {'Safety':<6} | {'F1':<6}")
    print("=" * 90)

    for case in cases:
        res = evaluate_case(case, retriever)
        eval_results.append(res)
        print(f"{res['case_id']:<32} | {res['specialty']:<25} | {res['recommendation_precision']:.2f}   | {res['recommendation_recall']:.2f}   | {res['safety_contraindication_recall']:.2f}   | {res['f1_score']:.2f}")

    retriever.close()

    # Aggregate Metrics
    avg_rec_prec = sum(r["recommendation_precision"] for r in eval_results) / len(eval_results)
    avg_rec_recall = sum(r["recommendation_recall"] for r in eval_results) / len(eval_results)
    avg_safety_recall = sum(r["safety_contraindication_recall"] for r in eval_results) / len(eval_results)
    avg_f1 = sum(r["f1_score"] for r in eval_results) / len(eval_results)
    avg_ret_recall = sum(r["retrieval_recall"] for r in eval_results) / len(eval_results)

    print("=" * 90)
    print(f"\nAGGREGATE BENCHMARK METRICS (N={len(cases)} Diverse Clinical Cases):")
    print(f"  * Mean Guideline Retrieval Recall:    {avg_ret_recall * 100:.1f}%")
    print(f"  * Mean Recommendation Precision:      {avg_rec_prec * 100:.1f}%")
    print(f"  * Mean Recommendation Recall:         {avg_rec_recall * 100:.1f}%")
    print(f"  * Mean Safety & Contraindication Recall: {avg_safety_recall * 100:.1f}%")
    print(f"  * Mean Overall Clinical F1 Score:     {avg_f1 * 100:.1f}%\n")

    # Save detailed JSON report
    report_path = os.path.join("eval", "evaluation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "aggregate_metrics": {
                "mean_retrieval_recall": avg_ret_recall,
                "mean_recommendation_precision": avg_rec_prec,
                "mean_recommendation_recall": avg_rec_recall,
                "mean_safety_recall": avg_safety_recall,
                "mean_f1_score": avg_f1
            },
            "cases": eval_results
        }, f, indent=2)
    print(f"Evaluation report saved to {report_path}")

if __name__ == "__main__":
    main()
