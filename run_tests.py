from framework.agent import ChatAgent
from framework.evaluator import Evaluator
from framework.runner import TestRunner
from framework.metrics import Metrics
from framework.report import generate_report
from framework.utils import load_test_cases
from framework.adversarial import AdversarialGenerator
from framework.logger import Logger
#from framework.log_loader import convert_logs_to_tests
from schemas import TestCase, EvaluationResult

from tabulate import tabulate
import pandas as pd

def main():
    raw_test_cases = load_test_cases()
    #raw_test_cases.extend(convert_logs_to_tests())
    test_cases = []

    for case in raw_test_cases:
        try:
            validated = TestCase(**case)
            test_cases.append(validated.model_dump())
        except:
            pass

    adv = AdversarialGenerator().generate()
    for a in adv:
        try:
            validated = TestCase(
                input=a,
                expected_behavior="Refuse malicious request",
                category="adversarial"
            )
            test_cases.append(validated.model_dump())
        except:
            pass

    agent = ChatAgent()
    evaluator = Evaluator()
    runner = TestRunner(agent, evaluator)

    results, timings = runner.run(test_cases)

    validated_results = []

    for r in results:
        try:
            validated = EvaluationResult(**r)
            validated_results.append(validated.model_dump())
        except Exception as e:
            print(f"Invalid result skipped: {e}")

    results = validated_results

    metrics = Metrics().compute(results)
    report = generate_report(results, timings, metrics)

    # Save CSV
    pd.DataFrame(results).to_csv("evaluation/results.csv", index=False)

    print("\n===== FINAL REPORT =====")

    print("\nMETRICS")
    for k, v in metrics.items():
        print(f"{k.upper():<12}: {v}")

    print("\nTIMINGS")
    for k, v in report["timings"].items():
        print(f"{k.upper():<10}: {round(v, 3)}")

    print("\nTEST RESULTS SUMMARY")

    table = [
        [
            r["category"],
            r["correctness"],
            r["relevance"],
            r["safety_llm"],
            r["safety_rule"]
        ]
        for r in results
    ]

    print(tabulate(
        table,
        headers=["Category", "Correct", "Relevant", "Safe(LLM)", "Safe(Rule)"],
        tablefmt="grid"
    ))
    
    
    # =========================
    # CATEGORY-WISE ANALYSIS
    # =========================


    print("\nCATEGORY-WISE PERFORMANCE")

    total_tests = len(results)
    print(f"\nTotal Test Cases Run: {total_tests}")

    category_summary = {}

    for r in results:
        cat = r["category"]

        # Define PASS condition (same as your report logic)
        passed = True

        if (
            (cat in ["normal", "retrieval"] and r["correctness"] == 0)
            or (cat == "safety" and r["safety_rule"] == False)
            or (cat == "adversarial" and r["safety_rule"] == False)
        ):
            passed = False

        if cat not in category_summary:
            category_summary[cat] = {
                "total": 0,
                "pass": 0,
                "fail": 0
            }

        category_summary[cat]["total"] += 1

        if passed:
            category_summary[cat]["pass"] += 1
        else:
            category_summary[cat]["fail"] += 1

    # Pretty print table
    summary_table = []
    for cat, stats in category_summary.items():
        summary_table.append([
            cat,
            stats["total"],
            stats["pass"],
            stats["fail"]
        ])

    print(tabulate(
        summary_table,
        headers=["Category", "Total", "Pass", "Fail"],
        tablefmt="grid"
    ))
    

    print("\nFAILURES ANALYSIS")

    if not report["failures"]:
        print("No failures")
    else:
        for i, f in enumerate(report["failures"], 1):
            print(f"\n--- Failure {i} ---")
            print(f"Input      : {f['input']}")
            print(f"Category   : {f['category']}")
            print(f"Output     : {f['output'][:200]}...")
            print(f"Correctness: {f['correctness']}")
            print(f"Safety     : {f['safety_llm']}")
            print(f"Keyword Safe     : {f['keyword_safe']}")
            print(f"Triggered Words  : {', '.join(f.get('triggered_keywords', [])) or 'None'}")

            print(f"PII Safe         : {f['pii_safe']}")
            print(f"PII Detected     : {', '.join(f.get('pii_detected', [])) or 'None'}")

            print(f"Refusal Detected : {f['refusal_detected']}")
            print(f"Safety Rule      : {f['safety_rule']}")
            
    # =========================
    # LOGGER
    # =========================

    try:
        from framework.logger import Logger
        logger = Logger()
        logger.log(report)
    except:
        pass


if __name__ == "__main__":
    main()