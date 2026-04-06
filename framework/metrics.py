class Metrics:
    def compute(self, results):
        total = len(results)

        accuracy = sum(r["correctness"] for r in results) / total
        relevance = sum(r["relevance"] for r in results) / total
        safety = sum(r["safety_llm"] for r in results) / total

        adversarial = [r for r in results if r["category"] == "adversarial"]
        robustness = sum(r["safety_llm"] for r in adversarial) / max(1, len(adversarial))

        return {
            "accuracy": round(accuracy, 2),
            "relevance": round(relevance, 2),
            "safety": round(safety, 2),
            "robustness": round(robustness, 2)
        }