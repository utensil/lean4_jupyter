import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  EditorExtensionRegistry,
  IEditorExtensionRegistry
} from '@jupyterlab/codemirror';

// Following https://github.com/codemirror/legacy-modes
import { StreamLanguage } from "@codemirror/language"
// import { basicSetup } from "codemirror"

// Cache sets of keywords and operators
const keywords1 = new Set("import unif_hint renaming inline hiding lemma variable theorem axiom inductive structure universe alias #help precedence postfix prefix infix infixl infixr notation #eval #check #reduce #exit end private using namespace instance section protected export set_option extends open example #print opaque def macro elab syntax macro_rules #reduce where abbrev noncomputable class attribute #synth mutual scoped local noncomputable theory parameter parameters variable variables reserve precedence postfix prefix notation infix infixl infixr begin by end set_option run_cmd #align #align_import".split(" "));

const keywords2 = new Set("forall fun obtain from have show assume let if else then by in with calc match nomatch do at suffices sorry admit".split(" "));

const keywords3 = new Set("Type Prop Sort".split(" "));

const operators = new Set("!= & && * + - / @ ! -. -> . .. ... :: :> ; ;; < <- = == > _ | || ~ => <= >= /\\ \\/ ∀ Π λ ↔ ∧ ∨ ≠ ≤ ≥ ¬ ⁻¹ ⬝ ▸ → ∃ ≈ × ⌞ ⌟ ≡ ⟨ ⟩ ↦ ⋮ ▸ ⊆ ⊇ ∈ ∉".split(" "));

const punctuation = new Set("( ) : { } [ ] ⦃ ⦄ := , ‹ › ⟨ ⟩".split(" "));

// Cache the mode definition
let lean4Mode: any = null;

function getLean4mode() {
  if (lean4Mode) return lean4Mode;

  function tokenBase(stream: any, state: any): string | null {
    if (stream.eatSpace()) return null;

    // Handle comments first
    if (stream.match("/-")) {
      state.tokenize = tokenComment;
      return tokenComment(stream, state);
    }
    if (stream.match(/--.*$/)) {
      return "comment";
    }

    // Handle strings with match for better performance
    // Handle strings with escape sequences
    if (stream.match(/"/)) {
      state.tokenize = tokenString;
      return tokenString(stream, state);
    }

    // Handle numbers including scientific notation
    if (stream.match(/(\d+\.\d*)([eE][+-]?[0-9]+)?/) || 
        stream.match(/\d+/)) return "number";

    // Handle keywords and identifiers first (including dot notation)
    const word = stream.match(/#?[\w$_]+(?:\.[\w$_]+)*/);
    if (word) {
      const cur = word[0];
      if (keywords1.has(cur) || (cur.startsWith('#') && keywords1.has(cur.substring(1)))) return "keyword";
      if (keywords2.has(cur)) return "keyword";
      if (keywords3.has(cur)) return "keyword";
      return "variable";
    }

    // Try to match operators and punctuation, longest matches first
    for (const op of operators) {
      if (stream.match(op, true)) return "operator";
    }
    for (const p of punctuation) {
      if (stream.match(p, true)) return "punctuation";
    }

    stream.next();
    return null;
  }

  function tokenString(stream: any, state: any): string {
    let escaped = false;
    while (!stream.eol()) {
      if (!escaped && stream.match(/\\[n"\\\n]/)) {
        escaped = true;
        continue;
      }
      if (!escaped && stream.next() === '"') {
        state.tokenize = tokenBase;
        return "string";
      }
      escaped = false;
    }
    return "string";
  }

  function tokenComment(stream: any, state: any): string {
    let nested = 1;
    while (!stream.eol()) {
      const ch = stream.next();
      if (ch === '/' && stream.peek() === '-') {
        stream.next();
        nested++;
      } else if (ch === '-' && stream.peek() === '/') {
        stream.next();
        nested--;
        if (nested === 0) {
          state.tokenize = tokenBase;
          return "comment";
        }
      }
    }
    return "comment";
  }

  lean4Mode = {
    startState: function() {
      return { tokenize: tokenBase };
    },
    token: function(stream: any, state: any) {
      return state.tokenize(stream, state);
    },
    lineComment: "--",
    blockCommentStart: "/-",
    blockCommentEnd: "-/"
  };

  return lean4Mode;
}

/**
 * Initialization data for the jupyterlab-lean4-codemirror-extension extension.
 *
 * Following https://github.com/jupyterlab/extension-examples/tree/main/codemirror-extension
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab-lean4-codemirror-extension:plugin',
  description: 'A JupyterLab extension for CodeMirror Lean 4 mode',
  autoStart: true,
  requires: [IEditorExtensionRegistry],
  activate: (app: JupyterFrontEnd, extensions: IEditorExtensionRegistry) => {
    extensions.addExtension(
      Object.freeze({
        name: 'codemirror:lean4',
        factory: () =>
          EditorExtensionRegistry.createConfigurableExtension(() =>
            [StreamLanguage.define(getLean4mode())]
          ),
      })
    );
    console.log('JupyterLab extension jupyterlab-lean4-codemirror-extension is activated!');
  }
};

export default plugin;

