#!/bin/bash
set -e

# Script purpose: prepare for local development

# get script parent directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_ROOT=$SCRIPT_DIR/..
REPL_HOME=$PROJECT_ROOT/.lean4_jupyter/repl

# force clean up
rm -rf $REPL_HOME
rm /usr/local/bin/repl

# repl is not bumped to leanprover/lean4:v4.8.0-rc2 yet
elan default leanprover/lean4:v4.8.0-rc1

# install the Lean REPL
$SCRIPT_DIR/install_repl.sh

if [ -z "$CI" ]; then
  # if the environment variable CI is not set
  # then use pyenv to switch to the correct python version
  pyenv shell 3.11
fi

# force uninstall alectryon
pip uninstall alectryon -y

# install the Lean4 Jupyter kernel
pip install -f -e "$PROJECT_ROOT[test]"
python -m lean4_jupyter.install

# prepare demo_proj
cd examples/demo_proj
lake exe cache get && lake build
