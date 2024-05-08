from ipykernel.kernelbase import Kernel
from pexpect import replwrap, EOF
import pexpect

from subprocess import check_output
import os.path
import uuid
import random
import string
import json

import re
import signal

__version__ = '0.0.1'

# Lean (version 4.7.0-rc2, aarch64-apple-darwin, commit 6fce8f7d5cd1, Release)
version_pat = re.compile(r'version (\d+(\.\d+)+(-rc\d+)?)')

# Based on https://github.com/zhangir-azerbayev/pySagredo/blob/main/pysagredo/gym/__init__.py
class Lean4Wrapper:
    def __init__(self):
        self.proc = pexpect.spawn("./repl", echo=True, encoding='utf-8', codec_errors='replace')
    
    def run_command(self, code, env=None, verbose=False, timeout=20):
        if env:
            command = (
                '{ "cmd" : "' + repr(code)[1:-1] + f'", "env" : {env}' + " }"
            )  # [1:-1] removes single quotes
        else:
            command = (
                '{ "cmd" : "' + repr(code)[1:-1] + '" }'
            )  # [1:-1] removes single quotes

        if verbose:
            print(command)
        self.proc.sendline(command)
        self.proc.expect_exact(command + "\r\n")

        # debugging
        # print(self.proc.before)

        self.proc.sendline()
        self.proc.expect_exact("\r\n")
        try:
            index = self.proc.expect('env": \d+\}', timeout=timeout)
            output = self.proc.before + self.proc.match.group()
            if verbose: 
                print(output)
            return json.loads(output)
        except pexpect.exceptions.TIMEOUT:
            self.proc.sendintr()
            interrupted = True
            return {"error": "FAILED DUE TO TIMEOUT", "buffer": self.proc.buffer}
        except KeyboardInterrupt:
            return {"error": "FAILED DUE TO KEYBOARD INTERRUPT", "buffer": self.proc.buffer}
        except EOF:
            return {"error": "FAILED DUE TO EOF", "buffer": self.proc.buffer}

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
                     'codemirror_mode': 'shell',  # TODO: fix code mirror mode
                     'mimetype': 'text/x-lean4',
                     'file_extension': '.lean'}

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        self._start_lean4()

    def _start_lean4(self):
        # Signal handlers are inherited by forked processes, and we can't easily
        # reset it from the subprocess. Since kernelapp ignores SIGINT except in
        # message handlers, we need to temporarily reset the SIGINT handler here
        # so that bash and its children are interruptible.
        old_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_DFL)
        # We need to temporarily reset the default signal handler for SIGPIPE so
        # that commands like `head` used in a pipe chain can signal to the data
        # producers. 
        old_sigpipe_handler = signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        try:
            self.leanwrapper = Lean4Wrapper()
        finally:
            signal.signal(signal.SIGINT, old_sigint_handler)
            signal.signal(signal.SIGPIPE, old_sigpipe_handler)

    def process_output(self, output):
        obj = output
        plain_output = json.dumps(obj)
        stream_content = {'name': 'stdout', 'text': plain_output}
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        interrupted = False
        # try:
        output = self.leanwrapper.run_command(code.strip(), timeout=None)
        self.process_output(output)

        if False: # TODO handle Lean returned error
            error_content = {
                'ename': '',
                'evalue': str(exitcode),
                'traceback': []
            }
            self.send_response(self.iopub_socket, 'error', error_content)

            error_content['execution_count'] = self.execution_count
            error_content['status'] = 'error'
            return error_content
        else:
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}
