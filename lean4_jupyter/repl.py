from typing import Any, Dict, DefaultDict, Optional, Tuple, Union, NamedTuple  # noqa: F401
from pexpect import EOF
import pexpect
from dataclasses import dataclass
from subprocess import check_output
import json
import re
import os


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

        if "proofState" in self.info:
            self.proofStates.append(self.info["proofState"])


class Lean4ReplWrapper:

    def launch():
        return pexpect.spawn("lake env repl",
                             echo=False, encoding='utf-8', codec_errors='replace')

    def init(self):
        self.check()
        self.repl = Lean4ReplWrapper.launch()
        self.state = Lean4ReplState()
        self.commands = {}
        self.expect_patterns = self.repl.compile_pattern_list([
            '\r\n\r\n',
            # pexpect.EOF,
            # pexpect.TIMEOUT,
            # pexpect.ExceptionPexpect
        ])

    def __init__(self):
        self.init()

    def shutdown(self):
        self.repl.terminate(force=True)

    def cd(self, path):
        os.chdir(path)
        self.shutdown()
        self.init()

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

    def comment_out_magic(self, code):
        # replace string matching regrex ^% with --%
        return re.sub(r'^%', '--%', code)

    def run_magic(self, code, timeout):
        # if code starts with --%load, load the file
        matched_load = re.match(r'^--%\s*load\s+(?P<path>[^\n]*)', code)
        if matched_load:
            path = matched_load.group('path')
            repl_io = self.load_file(path, timeout)
            return repl_io, self.handle_post_state(repl_io)

        return None, self.run_simple_magic(code, timeout)

    def run_simple_magic(self, code, timeout):
        # if code starts with --%cd, change the working directory
        matched_cd = re.match(r'^--%\s*cd\s+(?P<path>[^\n]*)', code)
        if matched_cd:
            path = matched_cd.group('path')
            self.cd(path)
            return Lean4ReplState()

        # if code starts with --% env, then reset the environment
        matched_env_reset = re.match(r'^--%\s*e(nv)?[^0-9]*\n', code)
        if matched_env_reset:
            return Lean4ReplState()

        # if code starts with --% proof, then use the last proofStates
        matched_proof = re.match(r'^--%\s*p(roof|rove)?[^0-9]*\n', code)
        if matched_proof:
            return self.state

        env = self.state.env
        proofStates = self.state.proofStates

        # if code is specified with --% env <env> or --% proof <proofState>,
        # then use the specified env and proofState
        matched = re.match(
            r'^--%\s*(e(nv)?[- ]*(?P<env>\d+)|p(roof|rove)?[- ]*(?P<prove>\d+))?', code)
        if matched:
            matched_env = matched.group('env')
            matched_prove = matched.group('prove')
            if matched_env is not None:
                env = int(matched_env)
            if matched_prove is not None:
                proofStates = [int(matched_prove)]

            return Lean4ReplState(env=env, proofStates=proofStates)

        # By default, ignore proofStates, use the last env, assuming this is a new command
        return Lean4ReplState(env=self.state.env)

    def send_and_recv(self, input, timeout):
        repl = self.repl
        repl.sendline(input)
        repl.sendline()
        repl.expect_list(self.expect_patterns, timeout=timeout)
        output = repl.before  # + repl.match.group()
        return output

    def load_file(self, file_path, timeout, all_tactics=True):
        input_dict = {
            "path": file_path,
            "allTactics": all_tactics
        }
        input = json.dumps(input_dict)
        output = self.send_and_recv(input, timeout)
        repl_io = Lean4ReplIO(input, output)
        return repl_io

    def handle_pre_state(self, state):
        # update the state as parsed before sending the input
        self.state = state

    def handle_post_state(self, repl_io):
        env = repl_io.output.env if repl_io.output.env is not None else self.state.env

        self.state = Lean4ReplState(
            env=env, proofStates=repl_io.output.proofStates)

        # TODO: for now, this would overwrite the previous command executed for the same env
        # Instead, this should be stored in a graph, thus could be displayed by a magic
        self.commands[env] = repl_io.input.info

        return self.state

    def run_command(self, code, timeout=-1):
        try:
            code = self.comment_out_magic(code)
            repl_io, state = self.run_magic(code, timeout)
            # For heavy magic, ignore the rest of code
            if repl_io is not None:
                return repl_io

            env = state.env
            repl = self.repl

            if len(state.proofStates) == 0:
                input_dict = {
                        "cmd": code
                }
                if env is not None:
                    input_dict["env"] = env
            else:
                # {"tactic": "apply Int.natAbs", "proofState": 0}
                input_dict = {
                    "tactic": code,
                    "proofState": max(state.proofStates)
                }
            input = json.dumps(input_dict)

            self.handle_pre_state(state)
            output = self.send_and_recv(input, timeout)
            repl_io = Lean4ReplIO(input, output)
            self.handle_post_state(repl_io)

            return repl_io
        # TODO the following should be rewritten to emit not dicts
        except pexpect.exceptions.TIMEOUT:
            repl.sendintr()
            return {"error": "FAILED DUE TO TIMEOUT", "buffer": repl.buffer}
        except KeyboardInterrupt:
            repl.sendintr()
            return {"error": "FAILED DUE TO KEYBOARD INTERRUPT", "buffer": repl.buffer}
        except EOF:
            return {"error": "FAILED DUE TO EOF", "buffer": repl.buffer}
        except:  # noqa: E722
            return {"error": "FAILED DUE TO UNKNOWN REASON", "buffer": repl.buffer}
