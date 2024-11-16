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
import { basicSetup } from "codemirror"

// Cache sets of keywords and operators
const keywords1 = new Set("import unif_hint renaming inline hiding lemma variable theorem axiom inductive structure universe alias #help precedence postfix prefix infix infixl infixr notation #eval #check #reduce #exit end private using namespace instance section protected export set_option extends open example #print opaque def macro elab syntax macro_rules #reduce where abbrev noncomputable class attribute #synth mutual scoped local noncomputable theory parameter parameters variable variables reserve precedence postfix prefix notation infix infixl infixr begin by end set_option run_cmd #align #align_import".split(" "));

const keywords2 = new Set("forall fun obtain from have show assume let if else then by in with calc match nomatch do at suffices sorry admit".split(" "));

const keywords3 = new Set("Type Prop Sort".split(" "));

const operators = new Set("!= # & && * + - / @ ! -. -> . .. ... :: :> ; ;; < <- = == > _ | || ~ => <= >= /\\ \\/ ∀ Π λ ↔ ∧ ∨ ≠ ≤ ≥ ¬ ⁻¹ ⬝ ▸ → ∃ ≈ × ⌞ ⌟ ≡ ⟨ ⟩ ↦ ⋮ ▸ ⊆ ⊇ ∈ ∉".split(" "));

const punctuation = new Set("( ) : { } [ ] ⦃ ⦄ := , ‹ › ⟨ ⟩".split(" "));

// Cache the mode definition
let lean4Mode: any = null;

function getLean4mode() {
  if (lean4Mode) return lean4Mode;

  function tokenBase(stream: any, state: any): string | null {
    if (stream.eatSpace()) return null;

    const ch = stream.next();
    if (ch === "/") {
      if (stream.eat("/")) {
        stream.skipToEnd();
        return "comment";
      }
      if (stream.eat("*")) {
        state.tokenize = tokenComment;
        return tokenComment(stream, state);
      }
    }

    if (ch === '"' || ch === "'") {
      state.tokenize = tokenString(ch);
      return state.tokenize(stream, state);
    }

    if (/\d/.test(ch)) {
      stream.eatWhile(/\d/);
      if (stream.eat(".")) {
        stream.eatWhile(/\d/);
      }
      return "number";
    }

    stream.eatWhile(/[\w\$_]/);
    const cur = stream.current();
    if (keywords1.has(cur)) return "keyword";
    if (keywords2.has(cur)) return "keyword";
    if (keywords3.has(cur)) return "keyword";
    if (operators.has(cur)) return "operator";
    if (punctuation.has(cur)) return "punctuation";

    return null;
  }

  function tokenComment(stream: any, state: any): string {
    while (!stream.eol()) {
      const ch = stream.next();
      if (ch === "*" && stream.eat("/")) {
        state.tokenize = tokenBase;
        break;
      }
    }
    return "comment";
  }

  function tokenString(quote: string) {
    return function(stream: any, state: any): string {
      let escaped = false, next;
      while ((next = stream.next()) !== null) {
        if (next === quote && !escaped) break;
        escaped = !escaped && next === "\\";
      }
      if (!escaped) state.tokenize = tokenBase;
      return "string";
    };
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
            [basicSetup, StreamLanguage.define(getLean4mode())]
          ),
      })
    );
    console.log('JupyterLab extension jupyterlab-lean4-codemirror-extension is activated!');
  }
};

export default plugin;

