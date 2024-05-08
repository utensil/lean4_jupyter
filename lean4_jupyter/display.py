from alectryon.core import Goal, Hypothesis, Message, Sentence, Text
from alectryon.serapi import annotate
from alectryon.pygments import make_highlighter
from alectryon.html import HtmlGenerator, HEADER

def get_annotated_html(repl_output_dict):
    # opam install coq-serapi
    # annotated = annotate(["Example xyz (H: False): True. (* ... *) exact I. Qed.", "Check xyz."])

    highlighter = make_highlighter("html", "coq") # coq, pygments_style)

    g = HtmlGenerator(highlighter=highlighter)
    return ("", g.gen([# A list of processed fragments
            [# Each fragment is a list of records (each an instance of a namedtuple)
            Sentence(contents='Example xyz (H: False): True.',
                    messages=[],
                    goals=[Goal(name=None,
                                conclusion='True',
                                hypotheses=[Hypothesis(names=['H'],
                                                        body=None,
                                                        type='False')])])
            ],
            [Sentence(contents=' (* ... *) ', messages=[], goals=[])],
            [Sentence(contents='exact I.', messages=[], goals=[])],
            [Sentence(contents=' ', messages=[], goals=[])],
            [Sentence(contents='Qed.', messages=[], goals=[])],
            [Sentence(contents='Check xyz.',
                    messages=[Message(contents='xyz\n     : False -> True')],
                    goals=[])]
        ])
    )