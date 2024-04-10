#!/bin/sh -e

set -x

ruff check app cli core --fix
ruff format app cli core
