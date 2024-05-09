# lean4_jupyter

A Lean 4 Jupyter kernel via [REPL](https://github.com/leanprover-community/repl).

## Status

Early stage of development.

What's working:

- The kernel is able to execute Lean 4 commands and echoes the input using alectryon style annotation [01_basic.ipynb](https://nbviewer.org/github/utensil/lean4_jupyter/blob/main/examples/01_basic.ipynb) with output messages.

## Installation

First, you need a working Lean 4 installation. You can install it via [elan](https://github.com/leanprover/elan).

Verify that `lean` and `lake` is in your `PATH`:

```bash
lean --version
lake --help|head -n 1
```

they should output Lean/Lake versions, respectively.

Then, you need to have a working `repl` in your `PATH`. You can build it from source:

```bash
mkdir -p ~/.lean4_jupyter
git clone https://github.com/leanprover-community/repl ~/.lean4_jupyter/repl
(cd ~/.lean4_jupyter/repl && echo '{ "cmd" : "def f := 2" }'|lake exe repl > /dev/null)
mv ~/.lean4_jupyter/repl/.lake/build/bin/repl /usr/local/bin/
```

Verify that `repl` is working:

```bash
echo '{"cmd": "#eval Lean.versionString"}'|repl
```

In case `repl` hangs, you could kill it with

```bash
ps aux|grep repl|grep -v grep|awk '{print $2}'|xargs kill -9
```

Then, ensure that you have `python`, `pip`, `jupyter` installed:

```bash
pip install jupyterlab
```

Then, install the kernel:

```bash
pip install lean4_jupyter
# or in development mode
pip install -e .
python -m lean4_jupyter.install
```

To use it, run one of:

```bash
jupyter notebook
jupyter lab
jupyter qtconsole --kernel lean4
jupyter console --kernel lean4
```

## Inspired by

- [Making simple Python wrapper kernels](https://jupyter-client.readthedocs.io/en/stable/wrapperkernels.html)
- [bash_kernel](https://github.com/takluyver/bash_kernel)
- [pySagredo](https://github.com/zhangir-azerbayev/pySagredo) (see also [repl#5](https://github.com/leanprover-community/repl/pull/5))
- [LeanDojo](https://github.com/lean-dojo/LeanDojo)
- [alectryon](https://github.com/cpitclaudel/alectryon?tab=readme-ov-file#as-a-library)
- [lean-lsp](https://github.com/utensil/lean-lsp) (My previous attempt to make a Lean 4 Jupyter kernel using Lean 4 LSP server)
