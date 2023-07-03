from typing import List
from report.benchmark_result import BenchmarkResult
import pandas as pd


class Report:
    """The report to write the benchmark results to"""

    __benchmark_results: List[BenchmarkResult] = []

    def add_benchmark_result(self, benchmark_result: BenchmarkResult):
        """Adds a benchmark result to the report

        Args:
            benchmark_result (BenchmarkResult): The benchmark result to add
        """
        self.__benchmark_results.append(benchmark_result)

    def write_report(self):
        """Writes the report to a csv file"""
        df = pd.DataFrame(self.__benchmark_results)
        df.to_csv("report.csv")
