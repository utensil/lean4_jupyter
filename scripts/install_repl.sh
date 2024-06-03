#!/bin/bash
set -e

# If you need to clean up before reinstalling
# rm -rf ~/.lean4_jupyter/repl
# rm /usr/local/bin/repl

# get script parent directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
mkdir -p .lean4_jupyter
# git clone -b fix-dup https://github.com/utensil/repl .lean4_jupyter/repl
git clone https://github.com/leanprover-community/repl .lean4_jupyter/repl
cd .lean4_jupyter/repl
lake build
# rm /usr/local/bin/repl
ln -s $DIR/../.lean4_jupyter/repl/.lake/build/bin/repl /usr/local/bin/repl
ls -lhta /usr/local/bin/repl
echo '{"cmd": "#eval Lean.versionString"}'|repl
