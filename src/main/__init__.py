"""A prompt for manual user input"""
import dataclasses
import time
import re

from yarl import cache_clear

import dagger
from dagger import object_type, function, dag, field, CacheSharingMode


@object_type
class Options:
    ci: bool = field(init=False, default=True)
    msg: str = field(init=False, default="Continue? (y/n)")
    input: str = field(init=False, default="n")
    match: str = field(init=False, default="y")
    choices: list[str] = field(default=list[str], init=False)

    @function
    def with_choices(self, choices: list[str]) -> "Options":
        self.choices = choices
        return self

    @function
    def with_msg(self, msg: str) -> "Options":
        self.msg = msg
        return self

    @function
    def with_input(self, input: str) -> "Options":
        self.input = input
        return self

    @function
    def with_match(self, match: str) -> "Options":
        self.match = match
        return self

    @function
    def with_ci(self, ci: bool) -> "Options":
        self.ci = ci
        return self


@object_type
class Result:
    outcome: bool = field()
    input: str = field()


@object_type
class Prompt:
    options: Options = field(default=Options, init=False)

    @function
    async def with_ci(self, ci: bool) -> "Prompt":
        self.options.ci = ci
        return self

    @function
    async def with_msg(self, msg: str) -> "Prompt":
        self.options.msg = msg
        return self

    @function
    async def with_input(self, input: str) -> "Prompt":
        self.options.input = input
        return self

    @function
    async def with_match(self, match: str) -> "Prompt":
        self.options.match = match
        return self

    @function
    async def with_choices(self, choices: list[str]) -> "Prompt":
        self.options.choices = choices
        return self

    @function
    async def execute(self) -> Result:
        if self.options.ci:
            if len(self.options.choices) > 0:
                return Result(
                    outcome=self.options.input in self.options.choices,
                    input=self.options.input)
            else:
                return Result(
                    outcome=re.search(pattern=self.options.match, string=self.options.input) is not None,
                    input=self.options.input)
        else:
            if len(self.options.choices) > 0:
                return await self.user_choice_reply
            else:
                return await self.user_text_reply()

    @property
    async def user_choice_reply(self):
        choices_str: str = " ".join(f"\"{choice}\"" for i, choice in enumerate(self.options.choices))
        script = f"""
                    #!/bin/sh
                    choices=({choices_str})                    
                    echo "{self.options.msg} (^C to abort)"
                    select choice in "${{choices[@]}}"; do
                        # choice being empty signals invalid input.
                        [[ -n $choice ]] || {{ echo "Invalid choice. Please try again." >&2; continue; }}
                        break # a valid choice was made, exit the prompt.
                    done
                    echo $choice > /tmp/prompt/input                    
                    """
        cache_buster = f"{time.time()}"
        cache = dag.cache_volume(key=cache_buster)

        response = await (dag.container()
                          .from_("bash")
                          .with_exec(["apk", "add", "--no-cache", "ncurses"])
                          .with_mounted_cache(path="/tmp/prompt", cache=cache)
                          .terminal(cmd=["bash", "-c", script])
                          .with_exec(["sh", "-c", f": {cache_buster} && exit 0"])
                          .with_exec(["cat", "/tmp/prompt/input"])
                          .stdout())

        return Result(
            outcome=self.options.choices.index(response.strip()) != -1,
            input=response)

    async def user_text_reply(self):
        cache_buster = f"{time.time()}"
        response: str = (await (dag
                                .container()
                                .from_("bash")
                                .with_mounted_cache("/tmp/prompt", dag.cache_volume(key=f"{time.time()}"))
                                .terminal(cmd=["sh", "-c", f"read -p '{self.options.msg} ' && echo $REPLY > /tmp/prompt/input"])
                                .with_exec(["sh", "-c", f": {cache_buster} && exit 0"])
                                .with_exec(["cat", "/tmp/prompt/input"])
                                .stdout())).strip()
        return Result(
            outcome=re.search(pattern=self.options.match, string=response) is not None,
            input=response)
