"""A prompt for manual user input"""
import time

import dagger
from dagger import object_type, function, dag, field


@object_type
class State:
    msg: str = field(default="Do you want to continue? (y/n)")
    input: str | None = field(default=None)
    outcome: bool = field(default=False)


@object_type
class Prompt:
    ci: bool = True
    """Whether the prompt is running in a CI environment"""

    input: str = ""
    """The user's input"""

    msg: str = "Do you want to continue? (y/n)"
    """The message to display to the user"""

    outcome: bool = False
    """The outcome of the prompt"""

    @function
    async def with_ci(self) -> "Prompt":
        self.ci = True
        return self

    @function
    async def with_msg(self, value: str) -> "Prompt":
        self.msg = value
        return self

    @function
    async def with_input(self, value: str) -> "Prompt":
        self.input = value
        return self

    @function
    async def prompt(self) -> "State":
        if self.ci:
            print('CI environment detected. Skipping terminal prompt.')
        else:
            response: str = await (dag.container().
                                   from_("alpine").
                                   with_mounted_cache("/tmp/prompt", dag.cache_volume(f"reply-{time.time()}")).
                                   terminal(cmd=["sh", "-c", f"read -p '{self.msg} ' && echo $INPUT > /tmp/prompt/input"]).
                                   with_exec(["echo", f"'cache buster {time.time()}'"]).
                                   with_exec(["cat", "/tmp/prompt/input"]).
                                   stdout())
            self.input = response

        self.outcome = self.input.find("y") != -1

        return State(msg=self.msg, input=self.input, outcome=self.outcome)
