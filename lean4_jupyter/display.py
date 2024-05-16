from typing import Any, Dict, DefaultDict, Optional, Tuple, Union, NamedTuple  # noqa: F401
from alectryon.core import Message, Sentence
from alectryon.pygments import make_highlighter
from alectryon.html import HtmlGenerator
import yaml
# import json
from .repl import Lean4ReplOutput, Lean4ReplState


class Lean4ReplOutputDisplay:

    HTML_HEADER = '''
        <link rel="stylesheet" href="https://lean-lang.org/lean4/doc/alectryon.css">
        <link rel="stylesheet" href="https://lean-lang.org/lean4/doc/pygments.css">
        <script src="https://lean-lang.org/lean4/doc/alectryon.js"></script>
        <script src="https://lean-lang.org/lean4/doc/highlight.js"></script>
        <style>
            @media (any-hover: hover) {
                .alectryon-io .alectryon-sentence:hover .alectryon-output,
                .alectryon-io .alectryon-token:hover .alectryon-type-info-wrapper,
                .alectryon-io .alectryon-token:hover .alectryon-type-info-wrapper {
                    position: unset;
                }
            }

            .highlight .w, .code .w {
                color: #d3d7cf;
                text-decoration: none;
            }

            body[data-jp-theme-light="false"] .alectryon-io .alectryon-goals,
            body[data-jp-theme-light="false"] .alectryon-io .alectryon-messages,
            body[data-jp-theme-light="false"] .alectryon-io .alectryon-goal,
            body[data-jp-theme-light="false"] .alectryon-io .alectryon-message {
                background: black;
            }
        </style>
    '''

    HTML_TEMPLATE = '''
        {header}
        <div class="alectryon-root alectryon-centered">
            {code}
        </div>
        <details>
            <summary>Raw input</summary>
            <code>{input_raw}</code>
        </details>
        <details>
            <summary>Raw output</summary>
            <code>{output_raw}</code>
        </details>{debug}
    '''

    def __init__(self, output: Lean4ReplOutput, state: Lean4ReplState = None):
        self.output = output
        self.state = state if state is not None else Lean4ReplState(
            env=output.env, proofStates=output.proofStates)
        self.message_dict = self._index_messages(self.output.info)
        self.output_yaml = yaml.safe_dump(self.output.info)

    def plain(self):
        output = self.output
        sentences = self._get_annotated_sentences(output.input, output.info, column=True)
        lines = []
        for sentence in sentences:
            for fragment in sentence:
                lines.append(fragment.contents)
                for message in fragment.messages:
                    lines.append(message.contents)
        raw = '\n\nRaw input:\n' + self.output.input.raw + '\nRaw output:\n' + self.output.raw
        return '\n'.join(lines) + raw

    def get_state_magics(self, state):
        magics = []

        if state.env is not None:
            magics.append(f'--% env {state.env}')
        if len(state.proofStates) > 0:
            magics.append(f'--% prove {max(state.proofStates)}')

        return magics

    def html(self):
        output = self.output
        fragments = self._get_annotated_html(output.input, output.info)
        self.output_alectryon = '\n'.join([fragment.render() for fragment in fragments])
        return self.HTML_TEMPLATE.format(
            header=self.HTML_HEADER,
            code=self.output_alectryon,
            input_raw=self.output.input.raw,  # yaml.safe_dump(output.input.info),
            output_raw=self.output.raw,  # self.output_yaml,
            debug=''
            # '''
            # <details>
            #     <summary>Message Index</summary>
            #     <code>{message_index}</code>
            # </details>'''.format(message_index=yaml.safe_dump(self.message_dict))
        )

    def _get_annotated_sentences(self, input, output_dict, column=False):
        sentences = []
        input_code = ''
        if 'cmd' in input.info:
            input_code = input.info['cmd']
        elif 'tactic' in input.info:
            input_code = input.info['tactic']
        elif 'path' in input.info:
            input_code = f'--% load {input.info["path"]}'
        else:
            raise ValueError(f'Invalid input: {input}')
        input_code_lines = input_code.split('\n')
        last_line_no = len(input_code_lines)
        for line_no, cmd_line in enumerate(input_code_lines, start=1):
            messages = []  # [Message(contents=f'This is line {line_no}')]
            if line_no in self.message_dict:
                for msg in self.message_dict[line_no]:
                    messages.append(Message(contents=self._render_message(msg, column)))
            # TODO: figure out why this is 0
            # This happens for tactics like `exact?` that output suggestions
            if line_no == last_line_no and 0 in self.message_dict:
                for msg in self.message_dict[0]:
                    messages.append(Message(contents=self._render_message(msg, column)))
            # For errors with no lineno, for goals accomplished
            if line_no == last_line_no and -1 in self.message_dict:
                for msg in self.message_dict[-1]:
                    messages.append(Message(contents=self._render_message(msg, column)))
            sentence = Sentence(contents=cmd_line, messages=messages, goals=[])
            sentences.append([sentence])

        for magic in self.get_state_magics(self.state):
            sentences.append([Sentence(contents=magic, messages=[], goals=[])])

        return sentences

    def _get_annotated_html(self, input, output_dict):
        highlighter = make_highlighter("html", "lean4")  # coq, pygments_style)
        sentences = self._get_annotated_sentences(input, output_dict)

        g = HtmlGenerator(highlighter=highlighter)
        return g.gen(sentences)

        # return g.gen([# A list of processed fragments
        #     [# Each fragment is a list of records (each an instance of a namedtuple)
        #     Sentence(contents='Example xyz (H: False): True.',
        #             messages=[],
        #             goals=[Goal(name=None,
        #                         conclusion='True',
        #                         hypotheses=[Hypothesis(names=['H'],
        #                                                 body=None,
        #                                                 type='False')])])
        #     ],
        #     [Sentence(contents=' (* ... *) ', messages=[], goals=[])],
        #     [Sentence(contents='exact I.', messages=[], goals=[])],
        #     [Sentence(contents=' ', messages=[], goals=[])],
        #     [Sentence(contents='Qed.', messages=[], goals=[])],
        #     [Sentence(contents='Check xyz.',
        #             messages=[Message(contents='xyz\n     : False -> True')],
        #             goals=[])]
        # ])

    def _index_messages(self, output_dict):
        index = {}
        if 'messages' in output_dict:
            for msg in output_dict['messages']:
                if 'endPos' in msg and msg['endPos'] is not None:
                    end_line = msg['endPos']['line']
                    if end_line not in index:
                        index[end_line] = []
                    index[end_line].append(msg)
                elif 'pos' in msg and msg['pos'] is not None:
                    end_line = msg['pos']['line']
                    if end_line not in index:
                        index[end_line] = []
                    index[end_line].append(msg)
                else:
                    raise ValueError(f'Invalid message: {msg}')
        if 'message' in output_dict:
            msg = output_dict['message']
            # TODO: fix dup
            if -1 not in index:
                index[-1] = []
                index[-1].append({
                    'severity': 'error',
                    'data': msg
                })

        if 'goals' in output_dict:
            if len(output_dict['goals']) == 0:
                if -1 not in index:
                    index[-1] = []
                    index[-1].append({
                        'severity': 'info',
                        'data': 'Goals accomplished! 🐙'
                    })
        return index

    def _render_message(self, msg, column=False):
        EMOJI_DICT = {
            'info': '',
            'warning': '🟨',
            'error': '❌'
        }

        codespan = ''

        bar = '─'

        if column:
            if 'endPos' in msg and msg['endPos'] is not None:
                between = msg['endPos']['column'] - msg['pos']['column']
                codespan = ' ' * (msg['pos']['column']) + bar * between
            elif 'pos' in msg and msg['pos'] is not None:
                codespan = bar * (msg['pos']['column'])
            else:
                codespan = ''

            codespan += '▶ '

        return f'''{codespan}{EMOJI_DICT[msg['severity']]} {msg['data']}'''
        # return f'''<div class="lj-msg-{msg['severity']}">{msg['data']}</div>'''
