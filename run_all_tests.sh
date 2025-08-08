#!/bin/bash
cd "$(dirname "$0")"

# Activate your virtualenv
source ../mybotenv/bin/activate

# Run all tests with coverage
pytest --cov=bot --cov-report=term --cov-report=html tests/
