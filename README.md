# lean4_jupyter

A Lean 4 Jupyter kernel via [REPL](https://github.com/leanprover-community/repl).

## Installation

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
