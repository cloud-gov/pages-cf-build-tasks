#!/bin/bash

set -e

pip install -e .
pip install pytest cryptography
pytest
