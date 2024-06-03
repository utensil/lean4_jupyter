#!/bin/bash
set -e

# Script purpose: local test
pytest -vv --durations=50 --nbval --nbval-kernel-name lean4 examples/

