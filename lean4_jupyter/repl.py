from typing import Any, Dict, DefaultDict, Optional, Tuple, Union, NamedTuple, NoReturn
from pexpect import EOF
import pexpect
from collections import namedtuple
from subprocess import check_output
import json

Lean4ReplInput = namedtuple('Lean4ReplInput', 'raw info')

class Lean4ReplIO:
    def __init__(self, input_raw, output_raw):
        self.input = Lean4ReplInput(input_raw, json.loads(input_raw))
        self.output = Lean4ReplOutput(output_raw, self.input)

class Lean4ReplOutput:
    def __init__(self, output_raw, input: Lean4ReplInput):
        self.raw = output_raw
        self.input = input
        self.info = json.loads(output_raw)
        self.env = self.info["env"]

# Based on https://github.com/zhangir-azerbayev/pySagredo/blob/main/pysagredo/gym/__init__.py
class Lean4ReplWrapper:

    def __init__(self):
        self.check()
        self.repl = pexpect.spawn("repl", echo=False, encoding='utf-8', codec_errors='replace')
        self.env = None
        self.commands = {}
        self.expect_patterns = self.repl.compile_pattern_list([
            '\r\n\r\n',
            # pexpect.EOF,
            # pexpect.TIMEOUT,
            # pexpect.ExceptionPexpect
        ])

    def check(self):
        # check if Lean is installed
        try:
            check_output(['lean', '--version'])
        except FileNotFoundError:
            raise FileNotFoundError("Lean is not installed. Please install Lean before using this kernel.")     
    
    def run_command(self, code, timeout=20):
        repl = self.repl
        command_dict = {
                "cmd": code,
                "env": self.env
        } # [1:-1] removes single quotes

        command = json.dumps(command_dict)
        repl.sendline(command)
        # repl.expect_exact(command + "\r\n")

        repl.sendline()
        # repl.expect_exact("\r\n")
        try:
            index = repl.expect_list(self.expect_patterns, timeout=timeout)
            output = repl.before # + repl.match.group()
            output_dict = json.loads(output)
            # output_dict['sent_raw'] = command
            output_dict['sent'] = command_dict
            output_dict['recv_raw'] = output

            repl_io = Lean4ReplIO(command, output)

            self.env = repl_io.output.env
            self.commands[self.env] = command_dict

            return repl_io
        except pexpect.exceptions.TIMEOUT:
            repl.sendintr()
            interrupted = True
            return {"error": "FAILED DUE TO TIMEOUT", "buffer": repl.buffer}
        except KeyboardInterrupt:
            return {"error": "FAILED DUE TO KEYBOARD INTERRUPT", "buffer": repl.buffer}
        except EOF:
            return {"error": "FAILED DUE TO EOF", "buffer": repl.buffer}