#!/bin/bash
set -e

# Script purpose: install the Lean REPL

# get script parent directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
mkdir -p .lean4_jupyter
# git clone -b fix-dup https://github.com/utensil/repl .lean4_jupyter/repl
# rm -rf .lean4_jupyter/repl
if [ -d ".lean4_jupyter/repl" ]; then
  (cd .lean4_jupyter/repl && git checkout master)
else
  git clone https://github.com/leanprover-community/repl .lean4_jupyter/repl
fi

cd .lean4_jupyter/repl
lake build
# if [ -f /usr/local/bin/repl ]; then
#   rm /usr/local/bin/repl
# fi
ln -s $DIR/../.lean4_jupyter/repl/.lake/build/bin/repl /usr/local/bin/repl
ls -lhta /usr/local/bin/repl
echo '{"cmd": "#eval Lean.versionString"}'|repl
