import time
from framework.logger import Logger

class TestRunner:
    def __init__(self, agent, evaluator):
        self.agent = agent
        self.evaluator = evaluator
        self.logger = Logger()  # added

    def run(self, test_cases):
        results = []
        timings = []

        for test in test_cases:
            start = time.time()

            output = self.agent.run(test["input"])
            result = self.evaluator.evaluate(test, output)

            end = time.time()

            results.append(result)
            timings.append(end - start)

            # LOG EACH RESULT
            self.logger.log(result)

        return results, timings