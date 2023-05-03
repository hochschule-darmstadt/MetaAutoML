# Benchmark Tool

This is a tool for benchmarking OMAML. It uses the grpc interface of the controller to start trainings and run predictions on the training results to then calculate a score for the predictions. Running this benchmark regularly enables tracking the performance of OMAML and how it (hopefully) improves during development (also see the [issue](https://github.com/hochschule-darmstadt/MetaAutoML/issues/172) that tracks the development of the benchmark).

## Getting Started

Make sure the following is installed:

1. Python 3.11
2. VSCode

Follow these steps to start coding:

1. Run one of the startvscode scripts to open a VSCode instance in the correct folder
2. Install the recommended extensions
3. Run one of the setupvenv scripts to initialize the python environment
4. Make sure the venv is selected in VSCode

## Debugging

Press F5 in VSCode

## Unit-Tests

Use the test explorer in VSCode
