#!/usr/bin/env bash

python3.9 -m venv .venv

./.venv/bin/pip3 install wheel
./.venv/bin/pip install -r requirements.txt
