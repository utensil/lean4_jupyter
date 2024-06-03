# JavaScript and CSS files from vendor

This directory contains JavaScript and CSS files from third-party vendors, plus a few custom files, they are depended on by generated Lean 4 Jupyter notebooks via [jsdelivr CDN for Github projects](https://www.jsdelivr.com/?docs=gh) so they should never be removed.

We list the vendor files and the URLs where they come from:

- `alectryon.css`: https://lean-lang.org/lean4/doc/alectryon.css
- `pygments.css`: https://lean-lang.org/lean4/doc/pygments.css
- `alectryon.js`: https://lean-lang.org/lean4/doc/alectryon.js
- `highlight.js`: https://lean-lang.org/lean4/doc/highlight.js

For their licenses, please check [alectryon](https://github.com/cpitclaudel/alectryon), [pygments](https://github.com/pygments/pygments), [highlightjs-lean](https://github.com/leanprover-community/highlightjs-lean).

The custom files are:

- `lean4_jupyter.css`: Custom CSS for the Jupyter notebook, fixing style issues of the vendor CSS files in Jupyter environment.
