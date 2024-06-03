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

# install the Lean REPL
$SCRIPT_DIR/install_repl.sh

# switch to a python virtual environment
pyenv shell 3.11

# force uninstall alectryon
pip uninstall alectryon -y

# install the Lean4 Jupyter kernel
pip install -e $PROJECT_ROOT
python -m lean4_jupyter.install
