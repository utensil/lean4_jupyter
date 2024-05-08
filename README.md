# lean4_jupyter

A Lean 4 Jupyter kernel via [REPL](https://github.com/leanprover-community/repl).

## Installation

First, you need a working Lean 4 installation. You can install it via [elan](https://github.com/leanprover/elan).

Verify that `lean` is in your `PATH`:

```bash
lean --version
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
- [LeanDojo](https://github.com/lean-dojo/LeanDojo)
- [pySagredo](https://github.com/zhangir-azerbayev/pySagredo)
- [alectryon](https://github.com/cpitclaudel/alectryon?tab=readme-ov-file#as-a-library)
