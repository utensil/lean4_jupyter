# lean4_jupyter

A Lean 4 Jupyter kernel via [repl](https://github.com/leanprover-community/repl).

[![PyPI](https://img.shields.io/pypi/v/lean4_jupyter.svg)](https://pypi.org/project/lean4_jupyter/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lean4_jupyter.svg)](https://pypi.org/project/lean4_jupyter/)
![PyPI - License](https://img.shields.io/pypi/l/lean4_jupyter)
![PyPI - Status](https://img.shields.io/pypi/status/lean4_jupyter)
[![Python CI](https://github.com/utensil/lean4_jupyter/actions/workflows/ci.yml/badge.svg)](https://github.com/utensil/lean4_jupyter/actions/workflows/ci.yml)
[![lint - flake8](https://img.shields.io/badge/lint-flake8-blue)](https://github.com/PyCQA/flake8)
[![Static Badge](https://img.shields.io/badge/test-nbval-purple)](https://github.com/computationalmodelling/nbval)
[![Maintainability](https://api.codeclimate.com/v1/badges/666a7d45d436a598df2b/maintainability)](https://codeclimate.com/github/utensil/lean4_jupyter/maintainability)

## What's already working

🔥 See it in action: [Tutorial notebook](https://nbviewer.org/github/utensil/lean4_jupyter/blob/18e8d701982d640aa443195f5ca287eec45313e3/examples/00_tutorial.ipynb?flush_cache=true).

The kernel can:

- execute Lean 4 commands (including definitions, theorems, etc.)
- execute Lean 4 tactics with magic like `% proof` immediately after a `sorry`ed theorem
- backtrack to earlier environment or proof states with magic like `% env 1` or `% prove 3`
- support magics like [`%cd`](https://nbviewer.org/github/utensil/lean4_jupyter/blob/v0.0.1/examples/01_cd.ipynb?flush_cache=true) or [`%load`](https://nbviewer.org/github/utensil/lean4_jupyter/blob/v0.0.1/examples/02_load.ipynb?flush_cache=true) (loading a file)
- support for importing modules from projects and their dependencies, e.g. `Mathlib` ( [demo](https://nbviewer.org/github/utensil/lean4_jupyter/blob/v0.0.1/examples/03_import.ipynb?flush_cache=true) ).

Output:

- In `jupyter notebook` and alike: echos the input annotated in [alectryon](https://github.com/cpitclaudel/alectryon?tab=readme-ov-file#as-a-library) style, at the corresponding line (not columns yet), with messages, proof states etc.
- In `jupyter console` and alike: echos the input annotated in [codespan](https://github.com/brendanzab/codespan) style, at the corresponding `line:column`, with messages, proof states etc.
- Raw `repl` input/output in JSON format can be inspected by click-to-expand in the WebUI.

The kernel code is linted by [flake8](https://github.com/PyCQA/flake8), and tested with [nbval](https://github.com/computationalmodelling/nbval) in CI.

## What's next

- Improve the syntax highlighting in the WebUI, currently it sees Lean 4 as Python
- Improve the alectryon annotation to support annotations in the middle of a line
- Provide a switch to use codespan instead of alectryon in the WebUI, or a way to see warnings and errors without hovering or clicking
- Provide a switch for raw `repl` input/output inspection as a magic, disable it by default
- Learn from [previous prototypes](https://leanprover.zulipchat.com/#narrow/stream/270676-lean4/topic/Prototype.3A.20Jupyter.20for.20Lean4) to improve UX
- Make magics like `%cd` and `%load` work more robustly
- Support show `tactics` after `%load`
- Add all `repl` test cases to the CI and set up coverage
- Improve UI in Jupyter Dark themes
- Support running lake commands via `%lake`, e.g. `%lake build`
- Better (streamed) feedback for long running commands such as `import`
- Support changing Lean toolchain and adding dependencies in an ad hoc manner
- Minimize emmitted HTML code
- Possibly use [@shikijs/twoslash](https://shiki.style/packages/twoslash#rendererrich) style annotation and no longer depends on alectryon
- Possibly change to [Aya](https://github.com/aya-prover/aya-dev/blob/main/cli-impl/src/test/resources/negative/PatCohError.txt) style annotation for plain text output
- Minor code refactor to smooth things out

If you are interested in one of these TODOs, or you have some other nice features in mind, you may raise the discussion by opening an issue or discuss it in the [Zulip topic](https://leanprover.zulipchat.com/#narrow/stream/113488-general/topic/lean4_jupyter.3A.20A.20Lean.204.20Jupyter.20kernel.20via.20repl).

## Installation

First, you need a working Lean 4 installation. You can install it via [elan](https://github.com/leanprover/elan).

Verify that `lean` and `lake` is in your `PATH`:

```bash
lean --version
lake --help|head -n 1
```

they should output Lean/Lake versions, respectively.

Then, you need to have a working `repl` in your `PATH`.

You can build it from source (please read and adjust them before executing) using the example script `scripts/install_repl.sh`.

Verify that `repl` is working:

```bash
echo '{"cmd": "#eval Lean.versionString"}'|repl
```

In case `repl` hangs, you could kill it with

```bash
ps aux|grep repl|grep -v grep|awk '{print $2}'|xargs kill -9
```

Then, ensure that you have `python`, `pip` installed, and install Jupyter:

```bash
pip install notebook
# or
# pip install jupyterlab
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

## Rationale

I've always wanted to do literate programming with Lean 4 in Jupyter, but Lean LSP and Infoview in VS Code has provided an immersive experience with immediate feedback, so I could never imagine a better way to interact with Lean 4, until interacting with repl makes me believe that _limitless backtrack_ is another feature that best accompanies the _reproducible interactivity_ of alectryon style annotations.

The idea came to me in an afternoon, and I thought it's technically trivial to implement overnight thanks to repl. It took me a bit longer to work out the logistics of UX and polish the code, but it's fun to see the potential.

## Inspired by

- [Making simple Python wrapper kernels](https://jupyter-client.readthedocs.io/en/stable/wrapperkernels.html)
- [bash_kernel](https://github.com/takluyver/bash_kernel)
- [pySagredo](https://github.com/zhangir-azerbayev/pySagredo) (see also [repl#5](https://github.com/leanprover-community/repl/pull/5))
- [LeanDojo](https://github.com/lean-dojo/LeanDojo)
- [alectryon](https://github.com/cpitclaudel/alectryon?tab=readme-ov-file#as-a-library)
- [codespan](https://github.com/brendanzab/codespan)
- [lean-lsp](https://github.com/utensil/lean-lsp) (My previous attempt to make a Lean 4 Jupyter kernel using Lean 4 LSP server)
