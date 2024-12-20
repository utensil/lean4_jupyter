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

## Features

🔥 See it in action: [Tutorial notebook](https://nbviewer.org/github/utensil/lean4_jupyter/blob/18e8d701982d640aa443195f5ca287eec45313e3/examples/00_tutorial.ipynb?flush_cache=true).

The kernel can:

- execute Lean 4 commands (including definitions, theorems, etc.)
- execute Lean 4 tactics with magic like `% proof` immediately after a `sorry`ed theorem
- backtrack to earlier environment or proof states with magic like `% env 1` or `% prove 3`
- support magics like [`%cd`](https://nbviewer.org/github/utensil/lean4_jupyter/blob/v0.0.1/examples/01_cd.ipynb?flush_cache=true) or [`%load`](https://nbviewer.org/github/utensil/lean4_jupyter/blob/v0.0.1/examples/02_load.ipynb?flush_cache=true) (loading a file)
- support for importing modules from projects and their dependencies, e.g. `Mathlib` ( [demo](https://nbviewer.org/github/utensil/lean4_jupyter/blob/v0.0.1/examples/03_import.ipynb?flush_cache=true) ).

Output:

- In `jupyter notebook` and alike:
    - echos the input annotated in [alectryon](https://github.com/cpitclaudel/alectryon?tab=readme-ov-file#as-a-library) style, at the corresponding line (not columns yet), with messages, proof states etc.
    - highlights Lean 4 syntax in code cells via a companion JuptyerLab extension `jupyterlab-lean4-codemirror-extension`
- In `jupyter console` and alike: echos the input annotated in [codespan](https://github.com/brendanzab/codespan) style, at the corresponding `line:column`, with messages, proof states etc.
- Raw `repl` input/output in JSON format can be inspected by click-to-expand in the WebUI.

The kernel code is linted by [flake8](https://github.com/PyCQA/flake8), and tested with [nbval](https://github.com/computationalmodelling/nbval) in CI.



## Getting started

### Prerequisites

1. A working Lean 4 installation. You can install it via [elan](https://github.com/leanprover/elan).

2. A working Python installation (e.g. 3.11). If using a virtual environment, activate it before installing the kernel.

### One-liner installation

The following script will install a `repl` of a compatible Lean 4 toolchain, the kernel, and prepare the demo Lean 4 project.

```bash
git clone https://github.com/utensil/lean4_jupyter.git && cd lean4_jupyter && ./scripts/prep.sh
```

Note: the script could remove an existing `repl`, and it assumes `/usr/local/bin` is in your `PATH`, it will also set the default Lean 4 toolchain to the same as the one used by the `repl` to ensure `repl` works outside projects. For installing the extension to highlight Lean 4 syntax in JupyterLab, it will also use nvm to install Node.js if it's not installed.

If you prefer manual installation, please read __Manual installation__ below.

The installation script creates a virtual environment in the `.venv` folder in the repo, and installs the kernel into it. You can activate the virtual environment with:

```bash
source .venv/bin/activate
```
Then use jupyter as usual.

### Usage

To use it, run one of:

```bash
# Web UI

# classic notebook
jupyter notebook
# JuptyerLab (recommended)
jupyter lab

# Console UI

# hint: use Ctrl-D and confirm with y to exit
jupyter console --kernel lean4
# hint: you need to run `pip install PyQt5 qtconsole` to install it
jupyter qtconsole --kernel lean4
```
then open notebooks in the `examples` folder to familiarize yourself with the basic usage.

### Manual installation

1. Verify that `lean` and `lake` are in your `PATH`:

```bash
lean --version
lake --help|head -n 1
```
they should output Lean/Lake versions, respectively. If not, you can install them via [elan](https://github.com/leanprover/elan).

2. Install a working `repl` in your `PATH`.

You can build it from source (please read and adjust them before executing) using the example script `scripts/install_repl.sh`.

3. Verify that `repl` is working:

```bash
echo '{"cmd": "#eval Lean.versionString"}'|repl
```

In case `repl` hangs, you could kill it with

```bash
ps aux|grep repl|grep -v grep|awk '{print $2}'|xargs kill -9
```

4. Ensure that you have `python`, `pip` installed, and install Jupyter:

```bash
pip install notebook
# or
# pip install jupyterlab
```

Install the kernel using one of these options:

```bash
# Option 1: Install from PyPI (see "Support matrix" for tested versions)
pip install lean4_jupyter

# Option 2 (recommended): Install latest version from repo
pip install git+https://github.com/utensil/lean4_jupyter.git

# Option 3: Install in development mode (after checking out repo)
# pip install -e .

# After installing, register the kernel
python -m lean4_jupyter.install
```

Verify the kernel installation with:

```bash
jupyter kernelspec list
```

#### (Optional) Installing the JupyterLab Extension

If you are using JupyterLab, you can install the JupyterLab extension to enhance your experience with Lean 4 syntax highlighting for code cells:

1. Ensure Node.js is installed (version 22.0.0 or higher):

```bash
node -v
```

2. Install Python dependencies:

```bash
pip install ipykernel jupyterlab jupyter_packaging
```

3. Clone the repository (if not already done) and install the extension:

```bash
git clone https://github.com/utensil/lean4_jupyter.git
cd lean4_jupyter/ext
jlpm install
jlpm build
pip install .
jupyter-labextension install .
```

4. Verify the installation:

```bash
jupyter-labextension list
```
## Rationale

I've always wanted to do literate programming with Lean 4 in Jupyter, but Lean LSP and Infoview in VS Code has provided an immersive experience with immediate feedback, so I could never imagine a better way to interact with Lean 4, until interacting with repl makes me believe that _limitless backtrack_ is another feature that best accompanies the _reproducible interactivity_ of alectryon style annotations.

The idea came to me in an afternoon, and I thought it's technically trivial to implement overnight thanks to repl. It took me a bit longer to work out the logistics of UX and polish the code, but it's fun to see the potential.

This also serves as a human-friendly way to understand how Lean 4 repl works, for integrating repl with ML systems.

## What's next

- Add support for [Quarto](https://quarto.org/), possibly integrate with [Molten](https://github.com/benlubas/molten-nvim) in Neovim
- Add support for [Incrementality](https://lean-lang.org/blog/2024-7-1-lean-490/), see also [repl#57](https://github.com/leanprover-community/repl/pull/57)
- Make use of [Goal State Diffing](https://leanprover.zulipchat.com/#narrow/channel/113488-general/topic/lean.2Envim/near/478572115)
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

## Inspired by

- [Making simple Python wrapper kernels](https://jupyter-client.readthedocs.io/en/stable/wrapperkernels.html)
- [bash_kernel](https://github.com/takluyver/bash_kernel)
- [pySagredo](https://github.com/zhangir-azerbayev/pySagredo) (see also [repl#5](https://github.com/leanprover-community/repl/pull/5))
- [LeanDojo](https://github.com/lean-dojo/LeanDojo)
- [alectryon](https://github.com/cpitclaudel/alectryon?tab=readme-ov-file#as-a-library)
- [codespan](https://github.com/brendanzab/codespan)
- [lean-lsp](https://github.com/utensil/lean-lsp) (My previous attempt to make a Lean 4 Jupyter kernel using Lean 4 LSP server)

## Support matrix

| `lean4_jupyter` | Tested Lean 4 toolchain | Tested Python version |
| --------------- | ----------------------- | --------------------  |
| 0.0.1           | v4.8.0-rc1              | 3.11.0                |
| 0.0.2           | v4.11.0                 | 3.11.0                 |
| 0.0.3-dev (git main)       | v4.11.0                 | 3.13.0 (jupyterlab: 4.3.0)                |

