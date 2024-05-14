from typing import Any, Dict, DefaultDict, Optional, Tuple, Union, NamedTuple  # noqa: F401
from ipykernel.kernelbase import Kernel

from subprocess import check_output
import os.path

import re
import signal
import yaml

from .repl import Lean4ReplOutput, Lean4ReplWrapper
from .display import Lean4ReplOutputDisplay

__version__ = '0.0.1'

# the default is user home directory + .lean4_jupyter
__lean4_jupyter_dir__ = os.path.join(os.path.expanduser('~'), '.lean4_jupyter')

# Lean (version 4.8.0-rc1, aarch64-apple-darwin, commit dcccfb73cb24, Release)
version_pat = re.compile(r'version (\d+(\.\d+)+(-rc\d+)?)')


class Lean4Kernel(Kernel):
    implementation = 'lean4_jupyter'
    implementation_version = __version__

    @property
    def language_version(self):
        m = version_pat.search(self.banner)
        return m.group(1)

    _banner = None

    @property
    def banner(self):
        if self._banner is None:
            self._banner = check_output(['lean', '--version']).decode('utf-8')
        return self._banner

    language_info = {'name': 'lean4',
                     'codemirror_mode': 'python',  # TODO: fix code mirror mode
                     'mimetype': 'text/x-lean4',
                     'file_extension': '.lean'}

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self._start_lean4()

    def _start_lean4(self):
        old_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_DFL)
        old_sigpipe_handler = signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        try:
            self.leanwrapper = Lean4ReplWrapper()
        finally:
            signal.signal(signal.SIGINT, old_sigint_handler)
            signal.signal(signal.SIGPIPE, old_sigpipe_handler)

    def process_output(self, output: Lean4ReplOutput):
        # TODO make input/output contain state
        o = Lean4ReplOutputDisplay(output, self.leanwrapper.state)
        # https://jupyterbook.org/en/stable/content/code-outputs.html#render-priority
        self.send_response(self.iopub_socket, 'display_data', {
            'metadata': {},
            'data': {
                'text/plain': o.plain(),
                'text/html': o.html()
            }
        })

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        # try:
        repl_io = self.leanwrapper.run_command(code, timeout=None)

        # TODO move this to repl or display
        if isinstance(repl_io, dict):
            self.send_response(self.iopub_socket, 'display_data', {
                'metadata': {},
                'data': {
                    'text/plain': yaml.safe_dump(repl_io),
                    'text/html': f'<pre>{yaml.safe_dump(repl_io)}</pre>'
                }
            })
            return {'status': 'error', 'execution_count': self.execution_count,
                    'ename': 'Error', 'evalue': 'Error', 'traceback': ['Error']}

        self.process_output(repl_io.output)

        return {'status': 'ok', 'execution_count': self.execution_count,
                'payload': [], 'user_expressions': {}}

    def do_shutdown(self, restart):
        self.leanwrapper.shutdown()
        return {'status': 'ok', 'restart': restart}
