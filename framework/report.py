import statistics

def generate_report(results, timings, metrics):

    failures = [
        r for r in results
        if (
            (r["category"] in ["normal", "retrieval"] and r["correctness"] == 0)
            or (r["category"] == "safety" and r["safety_rule"] == False)
            or (r["category"] == "adversarial" and r["safety_rule"] == False)
        )
    ]

    return {
        "metrics": metrics,
        "timings": {
            "mean": statistics.mean(timings),
            "median": statistics.median(timings),
            "max": max(timings),
            "min": min(timings)
        },
        "failures": failures
    }