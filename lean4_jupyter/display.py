from alectryon.core import Goal, Hypothesis, Message, Sentence, Text
from alectryon.serapi import annotate
from alectryon.pygments import make_highlighter
from alectryon.html import HtmlGenerator, HEADER
import json
import yaml

class ReplOutput:

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

            .lj-msg-info {
                background-color: #f0f0f0;
                border-left: 4px solid #4CAF50;
                padding: 8px;    
            }

            .lj-msg-warning {
                background-color: #f0f0f0;
                border-left: 4px solid #FF9800;
                padding: 8px;
            }

            .lj-msg-error {
                background-color: #f0f0f0;
                border-left: 4px solid #f44336;
                padding: 8px;
            }
        </style>
    '''

    HTML_TEMPLATE = '''
        {header}
        <p>Environment: {env}</p>
        <div class="alectryon-root alectryon-centered">
            {code}
            <details>
                <summary>Raw output</summary>
                <pre>{code_raw}</pre>
            </details>
        </div>
    '''

    def __init__(self, output_dict):
        self.message_dict = self._index_messages(output_dict)

        self.env = output_dict["env"]
        self.sent = output_dict["sent"]
        
        self.output_dict = output_dict
        self.output_dict['message_dict'] = self.message_dict
        self.output_yaml = yaml.dump(self.output_dict)

    def html(self):
        fragments = self._get_annotated_html(self.output_dict)
        self.output_alectryon = '\n'.join([fragment.render() for fragment in fragments])
        return self.HTML_TEMPLATE.format(header=self.HTML_HEADER, env=self.env, code=self.output_alectryon, code_raw=self.output_yaml)

    def _get_annotated_html(self, repl_output_dict):
        highlighter = make_highlighter("html", "lean4") # coq, pygments_style)
        sentences = []
        cmd = self.sent['cmd']
        for line_no, cmd_line in enumerate(cmd.split('\n'), start=1):
            messages = [] # [Message(contents=f'This is line {line_no}')]
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
            'warning': '⚠️',
            'error': '❌'
        }
        return f'''{EMOJI_DICT[msg['severity']]} {msg['data']}'''
        # return f'''<div class="lj-msg-{msg['severity']}">{msg['data']}</div>'''