# lean4_jupyter

A Lean 4 Jupyter kernel via [repl](https://github.com/leanprover-community/repl).

[![PyPI](https://img.shields.io/pypi/v/lean4_jupyter.svg)](https://pypi.org/project/lean4_jupyter/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lean4_jupyter.svg)](https://pypi.org/project/lean4_jupyter/)
![PyPI - License](https://img.shields.io/pypi/l/lean4_jupyter)
![PyPI - Status](https://img.shields.io/pypi/status/lean4_jupyter)
[![Python CI](https://github.com/utensil/lean4_jupyter/actions/workflows/ci.yml/badge.svg)](https://github.com/utensil/lean4_jupyter/actions/workflows/ci.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/666a7d45d436a598df2b/maintainability)](https://codeclimate.com/github/utensil/lean4_jupyter/maintainability) 

## Status

Alpha.

## What's already working

🔥 See it in action: [Tutorial notebook](https://nbviewer.org/github/utensil/lean4_jupyter/blob/main/examples/00_tutorial.ipynb?flush_cache=true).

The kernel can:

- execute Lean 4 commands
- execute Lean 4 tatics with magic like `% proof` immediately after a `sorry`ed theorem
- backtrack to earlier environment or proof states with magic like `% env 1` or `% prove 3`
- support magics like [`%cd`](https://nbviewer.org/github/utensil/lean4_jupyter/blob/main/examples/01_cd.ipynb?flush_cache=true) or [`%load`](https://nbviewer.org/github/utensil/lean4_jupyter/blob/main/examples/02_load.ipynb?flush_cache=true) (loading a file)
- support for importing modules from projects and their dependencies, e.g. `Mathlib` ( [demo](https://nbviewer.org/github/utensil/lean4_jupyter/blob/main/examples/03_import.ipynb?flush_cache=true) ).

Output:

- In `jupyter notebook` and alike: echos the input annotated in [alectryon](https://github.com/cpitclaudel/alectryon?tab=readme-ov-file#as-a-library) style, at the corresponding line (not columns yet), with messages, proof states
- In `jupyter console` and alike: echos the input annotated in [codespan](https://github.com/brendanzab/codespan) style, at the corresponding `line:column`, with messages, proof states

## What's next

- Fix [repl#40](https://github.com/leanprover-community/repl/issues/40) (PRed as [repl#41](https://github.com/leanprover-community/repl/issues/41))
- Improve the alectryon annotation to support annotations in the middle of a line
- Make magics like `%cd` and `%load` work more robustly
- Support show `tactics` after `%load`
- Add a CI based on [papermill](https://github.com/nteract/papermill/)
- Improve UI in Jupyter Dark themes
- Minor code refactor to smooth things out

## Installation

First, you need a working Lean 4 installation. You can install it via [elan](https://github.com/leanprover/elan).

Verify that `lean` and `lake` is in your `PATH`:

```bash
lean --version
lake --help|head -n 1
```

they should output Lean/Lake versions, respectively.

Then, you need to have a working `repl` in your `PATH`.

You can build it from source (please read and adjust them before executing):

```bash
# If you need to clean up before reinstalling
# rm -rf ~/.lean4_jupyter/repl
# rm /usr/local/bin/repl

# Prepare a directory for lean4_jupyter where we install repl to
mkdir -p ~/.lean4_jupyter

# Before repl#41 merge, you might need to use this branch instead
git clone -b fix-dup https://github.com/utensil/repl ~/.lean4_jupyter/repl
# git clone https://github.com/leanprover-community/repl ~/.lean4_jupyter/repl

# Build repl
(cd ~/.lean4_jupyter/repl && lake build)

# Install repl to a place in your PATH, so less hassle of fiddling with PATH
ln -s ~/.lean4_jupyter/repl/.lake/build/bin/repl /usr/local/bin/repl
```

Verify that `repl` is working:

```bash
echo '{"cmd": "#eval Lean.versionString"}'|repl
```

In case `repl` hangs, you could kill it with

```bash
ps aux|grep repl|grep -v grep|awk '{print $2}'|xargs kill -9
```

Then, ensure that you have `python`, `pip`, `jupyter` installed, and run:

```bash
pip install jupyterlab
```

Then, install the kernel:

```bash
pip install lean4_jupyter
# or in development mode, check out the repo then run
# pip install -e .
python -m lean4_jupyter.install
```

To use it, run one of:

```bash
# Web UI
jupyter notebook
jupyter lab

# Console UI
# hint: use Ctrl-D and confirm with y to exit
jupyter console --kernel lean4
# hint: you need to run `pip install PyQt5 qtconsole` to install it
jupyter qtconsole --kernel lean4
```

## Inspired by

- [Making simple Python wrapper kernels](https://jupyter-client.readthedocs.io/en/stable/wrapperkernels.html)
- [bash_kernel](https://github.com/takluyver/bash_kernel)
- [pySagredo](https://github.com/zhangir-azerbayev/pySagredo) (see also [repl#5](https://github.com/leanprover-community/repl/pull/5))
- [LeanDojo](https://github.com/lean-dojo/LeanDojo)
- [alectryon](https://github.com/cpitclaudel/alectryon?tab=readme-ov-file#as-a-library)
- [codespan](https://github.com/brendanzab/codespan)
- [lean-lsp](https://github.com/utensil/lean-lsp) (My previous attempt to make a Lean 4 Jupyter kernel using Lean 4 LSP server)
