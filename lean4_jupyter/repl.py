from typing import Any, Dict, DefaultDict, Optional, Tuple, Union, NamedTuple  # noqa: F401
from pexpect import EOF
import pexpect
from dataclasses import dataclass
from subprocess import check_output
import json
import re


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
        try:
            # check if Lean is installed
            check_output(['lean', '--version'])
            # check if repl is installed
            check_output(["/bin/sh", "-c",
                          '''echo '{"cmd": "#eval Lean.versionString"}'|repl'''])
        except FileNotFoundError:
            raise RuntimeError("lean or repl is not properly installed, please follow README in "
                               "https://github.com/utensil/lean4_jupyter to install them.")

    def comment_out_native_magic(self, code):
        # replace string matching regrex ^% with --%
        return re.sub(r'^%', '--%', code)

    def parse_state_magic(self, code):
        matched = re.match(r'^--% e-(\d+)( p-(\d+))?', code)
        if matched:
            env = int(matched.group(1))
            return {
                "env": env
            }

        return {}

    def run_command(self, code, timeout=-1):
        code = self.comment_out_native_magic(code)
        state = self.parse_state_magic(code)
        env = self.env
        if 'env' in state:
            env = state['env']

        repl = self.repl
        command_dict = {
                "cmd": code,
                "env": env
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
