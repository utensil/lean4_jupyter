#!/bin/bash
set -e

# Script purpose: regenerate notebooks

# get script parent directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_ROOT=$SCRIPT_DIR/..
REPL_HOME=$PROJECT_ROOT/.lean4_jupyter/repl

# for all files in examples/ that have the extension .ipynb
for file in $PROJECT_ROOT/examples/*.ipynb; do
  # regenerate the notebook # --log-level DEBUG
  python -m papermill --cwd $PROJECT_ROOT/examples --kernel lean4 $file $file
  # run the above in one sed line
  sed -i '' '/"input_path": "/d;/"output_path": "/d' $file
done
