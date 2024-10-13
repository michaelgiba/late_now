#!/bin/bash

set -euxo pipefail

# Get the directory relative to this script
PROJECT_ROOT=$(dirname "$(readlink -f "$0")")
MODELS_ROOT="$PROJECT_ROOT/python/models"
ANIPORTRAIT_ROOT="$MODELS_ROOT/AniPortrait"
MOMASK_ROOT="$MODELS_ROOT/momask-codes"

# AniPortrait
if [ ! -d "$ANIPORTRAIT_ROOT" ]; then
  git clone https://github.com/michaelgiba/AniPortrait "$ANIPORTRAIT_ROOT"
  virtualenv -ppython3.10 "$ANIPORTRAIT_ROOT/.venv"
  source "$ANIPORTRAIT_ROOT/.venv/bin/activate"
  pip install -r "$ANIPORTRAIT_ROOT/requirements.txt"
  deactivate
fi

# momask-codes
if [ ! -d "$MOMASK_ROOT" ]; then
  git clone https://github.com/michaelgiba/momask-codes "$MOMASK_ROOT"
  virtualenv -ppython3.10 "$MOMASK_ROOT/.venv"
  source "$MOMASK_ROOT/.venv/bin/activate"
  pip install -r "$MOMASK_ROOT/requirements.txt"
  deactivate  
fi

virtualenv -ppython3.10 "$PROJECT_ROOT/.venv"
source "$PROJECT_ROOT/.venv/bin/activate"
pip install -r "$PROJECT_ROOT/requirements.txt"
deactivate
