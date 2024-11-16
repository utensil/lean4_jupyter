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

const operators = new Set("!= # & && * + - / @ ! -. -> . .. ... :: :> ; ;; < <- = == > _ | || ~ => <= >= /\\ \\/ ∀ Π λ ↔ ∧ ∨ ≠ ≤ ≥ ¬ ⁻¹ ⬝ ▸ → ∃ ≈ × ⌞ ⌟ ≡ ⟨ ⟩ ↦ ⋮ ▸ ⊆ ⊇ ∈ ∉".split(" "));

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

    // Handle strings with match for better performance
    if (stream.match(/"[^"]*"/)) return "string";
    if (stream.match(/'[^']*'/)) return "string";

    // Handle numbers more efficiently
    if (stream.match(/\d+(\.\d+)?/)) return "number";

    // Try to match longer operators first
    const opMatch = stream.match(/[!@#$%^&*+\-=<>?/\\|:;.,]+/);
    if (opMatch) {
      const op = opMatch[0];
      if (operators.has(op)) return "operator";
      if (punctuation.has(op)) return "punctuation";
    }

    // Handle keywords and identifiers
    const word = stream.match(/[\w$_]+/);
    if (word) {
      const cur = word[0];
      if (keywords1.has(cur)) return "keyword";
      if (keywords2.has(cur)) return "keyword";
      if (keywords3.has(cur)) return "keyword";
    }

    stream.next();
    return null;
  }

  function tokenComment(stream: any, state: any): string {
    const maxChars = 10000; // Prevent infinite loops
    let chars = 0;
    
    while (!stream.eol() && chars < maxChars) {
      chars++;
      if (stream.match("-/")) {
        state.tokenize = tokenBase;
        return "comment";
      }
      stream.next();
    }
    
    if (chars >= maxChars) {
      state.tokenize = tokenBase;
    }
    return "comment";
  }

  // Strings are now handled directly in tokenBase for better performance
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

