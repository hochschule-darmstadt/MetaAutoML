from report.benchmark_result import BenchmarkResult


class Report:
    __benchmark_results: list[BenchmarkResult] = []

    def add_benchmark_result(self, benchmark_result: BenchmarkResult):
        self.__benchmark_results.append(benchmark_result)

    def write_report(self):
        pass
