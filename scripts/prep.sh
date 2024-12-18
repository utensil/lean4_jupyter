#!/bin/bash
set -e

# Script purpose: prepare for local development

# get script parent directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_ROOT=$SCRIPT_DIR/..
REPL_HOME=$PROJECT_ROOT/.lean4_jupyter/repl
VENV_DIR=$PROJECT_ROOT/.venv

# Only create/use venv if not in CI
if [ -z "$CI" ]; then
  if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
  fi

  echo "Activating virtual environment..."
  source "$VENV_DIR/bin/activate"
  PIP="$VENV_DIR/bin/pip"
  PYTHON="$VENV_DIR/bin/python"
else
  PIP="pip"
  PYTHON="python"
fi

# force clean up
rm -rf "$REPL_HOME" || echo "No .lean4_jupyter/repl to clean up"
rm /usr/local/bin/repl || echo "No /usr/local/bin/repl to clean up"

# NOTE: this has to be the same as repl at all times
# setting default is a hack, to avoid issues of not having the right version
elan default leanprover/lean4:v4.11.0

# install the Lean REPL
"$SCRIPT_DIR"/install_repl.sh

# if [ -z "$CI" ]; then
#   # if the environment variable CI is not set
#   # then use pyenv to switch to the correct python version
#   pyenv shell 3.11
# fi

# force uninstall alectryon
"$PIP" uninstall alectryon -y

# install the Lean4 Jupyter kernel
(cd "$PROJECT_ROOT" && "$PIP" install -e '.[test]')
"$PYTHON" -m lean4_jupyter.install --user

# # Install ipykernel in virtual environment
# "$VENV_DIR/bin/pip" install ipykernel
# "$VENV_DIR/bin/python" -m ipykernel install --user --name="lean4_jupyter_dev"

# Install the JupyterLab extension
"$SCRIPT_DIR"/install_ext.sh

# prepare demo_proj
cd examples/demo_proj
lake exe cache get && lake build
