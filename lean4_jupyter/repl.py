from typing import Any, Dict, DefaultDict, Optional, Tuple, Union, NamedTuple  # noqa: F401
from pexpect import EOF
import pexpect
from dataclasses import dataclass
from subprocess import check_output
import json
import re


class Lean4ReplState:
    def __init__(self, env: Optional[int] = None, proofStates: list[int] = []):
        self.env = env
        self.proofStates = proofStates


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

        self.env = None
        if "env" in self.info:
            self.env = self.info["env"]

        self.proofStates = []
        if "sorries" in self.info:
            self.proofStates = [goal["proofState"] for goal in self.info["sorries"]]


class Lean4ReplWrapper:

    def __init__(self):
        self.check()
        self.repl = pexpect.spawn("repl", echo=False, encoding='utf-8', codec_errors='replace')
        self.state = Lean4ReplState()
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
        # if code starts with --% proof, then use the last proofStates
        matched_proof = re.match(r'^--% proof', code)
        if matched_proof:
            return self.state

        # if code is specified with --% e-<env> or --% p-<proofState>,
        # then use the specified env and proofState
        matched = re.match(r'^--% (e-(\d+)|p-(\d+))?', code)
        if matched:
            if matched.group(2) is not None:
                env = int(matched.group(2))
                proofStates = []
            if matched.group(3) is not None:
                env = None
                proofStates = [int(matched.group(3))]

            return Lean4ReplState(env=env, proofStates=proofStates)

        # By default, ignore proofStates, use the last env, assuming this is a new command
        return Lean4ReplState(env=self.state.env)

    def run_command(self, code, timeout=-1):
        code = self.comment_out_native_magic(code)
        state = self.parse_state_magic(code)
        env = state.env
        repl = self.repl

        if len(state.proofStates) == 0:
            input_dict = {
                    "cmd": code,
                    "env": env
            }

        else:
            # {"tactic": "apply Int.natAbs", "proofState": 0}
            input_dict = {
                "tactic": code,
                "proofState": max(state.proofStates)
            }
        input = json.dumps(input_dict)
        repl.sendline(input)

        repl.sendline()
        try:
            repl.expect_list(self.expect_patterns, timeout=timeout)
            output = repl.before  # + repl.match.group()
            repl_io = Lean4ReplIO(input, output)

            self.state = Lean4ReplState(
                env=repl_io.output.env, proofStates=repl_io.output.proofStates)

            # TODO: for now, this would overwrite the previous command executed for the same env
            # Instead, this should be stored in a graph, thus could be displayed by a magic
            self.commands[repl_io.output.env] = input_dict

            return repl_io
        # TODO the following should be rewritten to emit not dicts
        except pexpect.exceptions.TIMEOUT:
            repl.sendintr()
            return {"error": "FAILED DUE TO TIMEOUT", "buffer": repl.buffer}
        except KeyboardInterrupt:
            return {"error": "FAILED DUE TO KEYBOARD INTERRUPT", "buffer": repl.buffer}
        except EOF:
            return {"error": "FAILED DUE TO EOF", "buffer": repl.buffer}
