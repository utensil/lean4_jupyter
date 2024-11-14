
/// <reference path="../node_modules/@jupyterlab/codemirror/typings/codemirror/codemirror.d.ts" />

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  ICodeMirror
} from '@jupyterlab/codemirror';

// import { defineMode, defineMIME } from 'codemirror';

function defineLean4mode(code_mirror: any) {

  function words(str: string): { [key: string]: boolean } {
    const obj: { [key: string]: boolean } = {};
    const wordsArray = str.split(" ");
    for (const word of wordsArray) {
      obj[word] = true;
    }
    return obj;
  }

  const keywords1 = words("import unif_hint renaming inline hiding lemma variable theorem axiom inductive structure universe alias #help precedence postfix prefix infix infixl infixr notation #eval #check #reduce #exit end private using namespace instance section protected export set_option extends open example #print opaque def macro elab syntax macro_rules #reduce where abbrev noncomputable class attribute #synth mutual scoped local");
  const keywords2 = words("forall fun obtain from have show assume let if else then by in with calc match nomatch do at");
  const keywords3 = words("Type Prop Sort");
  const operators = words("!= # & && * + - / @ ! -. -> . .. ... :: :> ; ;; < <- = == > _ | || ~ => <= >= /\\ \\/ ∀ Π λ ↔ ∧ ∨ ≠ ≤ ≥ ¬ ⁻¹ ⬝ ▸ → ∃ ≈ × ⌞ ⌟ ≡ ⟨ ⟩ ↦");
  const punctuation = words("( ) : { } [ ] ⦃ ⦄ := ,");

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
      if (stream.eat(".")) stream.eatWhile(/\d/);
      return "number";
    }

    stream.eatWhile(/[\w\$_]/);
    const cur = stream.current();
    if (keywords1.hasOwnProperty(cur)) return "keyword";
    if (keywords2.hasOwnProperty(cur)) return "keyword";
    if (keywords3.hasOwnProperty(cur)) return "keyword";
    if (operators.hasOwnProperty(cur)) return "operator";
    if (punctuation.hasOwnProperty(cur)) return "punctuation";

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

  code_mirror.defineMode("lean4", function() {
    return {
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
  });

  code_mirror.defineMIME("text/x-lean4", "lean4");

  code_mirror.modeInfo.push({
    ext: ['lean'],
    mime: 'text/x-lean4',
    mode: 'lean4',
    name: 'Lean 4'
  });
}


const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab_prolog_codemirror_extension:plugin',
  autoStart: true,
  requires: [ICodeMirror],
  activate: (app: JupyterFrontEnd, codeMirror: ICodeMirror) => {
    defineLean4mode(codeMirror.CodeMirror);
    console.log('JupyterLab extension for Lean 4 mode is activated!');
  }
};


export default plugin;
