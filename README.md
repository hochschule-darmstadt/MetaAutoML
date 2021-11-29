# Repository for the Controller component of OMA-ML

This repository contains the controller segment of OMA-ML:

![](https://github.com/hochschule-darmstadt/MetaAutoML-Controller/blob/main/docs/images/controller-overview.png)

## Installation

Clone the repository and setup a local project using the requirements.txt for an local python enviromnent.

## Project Overview

- `Controller_pb2_grpc.py` is the RPC interface for the RPC server running in the controller, which is accessible for the frontend.
- `Adapter_pb2_grpc.py` is the RPC interface running in the adapters, which is then called by the controller.
