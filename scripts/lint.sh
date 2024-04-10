#!/usr/bin/env bash

set -e
set -x

# mypy app cli core
ruff check app cli core
ruff format app cli core --check
