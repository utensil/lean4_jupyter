from typing import Any, Dict, DefaultDict, Optional, Tuple, Union, NamedTuple  # noqa: F401
from alectryon.core import Message, Sentence
from alectryon.pygments import make_highlighter
from alectryon.html import HtmlGenerator
import yaml
from .repl import Lean4ReplOutput


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
        </style>
    '''

    HTML_TEMPLATE = '''
        {header}
        <div class="alectryon-root alectryon-centered">
            {code}
        </div>
        <details>
            <summary>Details</summary>
            <p>State: <code>{state}</code></p>
            <details>
                <summary>Raw input</summary>
                <code>{input_raw}</code>
            </details>
            <details>
                <summary>Raw output</summary>
                <code>{output_raw}</code>
            </details>
        </details>
    '''

    def __init__(self, output: Lean4ReplOutput):
        self.output = output
        self.message_dict = self._index_messages(self.output.info)
        self.output_yaml = yaml.safe_dump(self.output.info)

    def plain(self):
        return self.output.raw

    def html(self):
        output = self.output
        fragments = self._get_annotated_html(output.input, output.info)
        self.output_alectryon = '\n'.join([fragment.render() for fragment in fragments])
        return self.HTML_TEMPLATE.format(
            header=self.HTML_HEADER,
            state=f'--% e-{output.env}',
            code=self.output_alectryon,
            input_raw=self.output.input.raw,  # yaml.safe_dump(output.input.info),
            output_raw=self.output.raw  # self.output_yaml
        )

    def _get_annotated_html(self, input, output_dict):
        highlighter = make_highlighter("html", "lean4")  # coq, pygments_style)
        sentences = []
        cmd = input.info['cmd']
        for line_no, cmd_line in enumerate(cmd.split('\n'), start=1):
            messages = []  # [Message(contents=f'This is line {line_no}')]
            if line_no in self.message_dict:
                for msg in self.message_dict[line_no]:
                    messages.append(Message(contents=self._render_message(msg)))
            sentence = Sentence(contents=cmd_line, messages=messages, goals=[])
            sentences.append([sentence])

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
                end_line = msg['endPos']['line']
                if end_line not in index:
                    index[end_line] = []
                index[end_line].append(msg)
        return index

    def _render_message(self, msg):
        EMOJI_DICT = {
            'info': '',
            'warning': '🟨',
            'error': '❌'
        }
        return f'''{EMOJI_DICT[msg['severity']]} {msg['data']}'''
        # return f'''<div class="lj-msg-{msg['severity']}">{msg['data']}</div>'''
