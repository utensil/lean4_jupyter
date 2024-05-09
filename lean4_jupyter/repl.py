from typing import Any, Dict, DefaultDict, Optional, Tuple, Union, NamedTuple  # noqa: F401
from pexpect import EOF
import pexpect
from dataclasses import dataclass
from subprocess import check_output
import json


@dataclass
class Lean4ReplInput:
    raw: str
    info: Dict[str, Any]


class Lean4ReplIO:
    def __init__(self, input_raw: str, output_raw: str):
        self.input = Lean4ReplInput(input_raw, json.loads(input_raw))
        self.output = Lean4ReplOutput(output_raw, self.input)


class Lean4ReplOutput:
    def __init__(self, output_raw: str, input: Lean4ReplInput):
        self.raw = output_raw
        self.input = input
        self.info = json.loads(output_raw)
        self.env = self.info["env"]


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
            raise FileNotFoundError(
                "Lean is not installed. Please install Lean before using this kernel."
            )

    def run_command(self, code, timeout=20):
        repl = self.repl
        command_dict = {
                "cmd": code,
                "env": self.env
        }

        command = json.dumps(command_dict)
        repl.sendline(command)

        repl.sendline()
        try:
            repl.expect_list(self.expect_patterns, timeout=timeout)
            output = repl.before  # + repl.match.group()
            repl_io = Lean4ReplIO(command, output)

            self.env = repl_io.output.env
            self.commands[self.env] = command_dict

            return repl_io
        except pexpect.exceptions.TIMEOUT:
            repl.sendintr()
            return {"error": "FAILED DUE TO TIMEOUT", "buffer": repl.buffer}
        except KeyboardInterrupt:
            return {"error": "FAILED DUE TO KEYBOARD INTERRUPT", "buffer": repl.buffer}
        except EOF:
            return {"error": "FAILED DUE TO EOF", "buffer": repl.buffer}
