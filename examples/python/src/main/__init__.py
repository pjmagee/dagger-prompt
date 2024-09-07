"""Example of a Prompt module"""

import dagger
from dagger import dag, function, object_type


@object_type
class Examples:
    """Examples of prompts"""

    @function
    async def Prompt_Default(self) -> dagger.Container:
        prompt: dagger.PromptState = dag.prompt().prompt()  # CI is true by default
        outcome = await prompt.outcome()  # False because no input was provided

        if outcome:
            return dag.container().from_("alpine").with_exec(cmd=["echo", "Deploying..."])
        else:
            return dag.container().from_("alpine").with_exec(cmd=["echo", "Skipping deployment..."])

    @function
    async def Prompt_Input(self) -> dagger.Container:
        prompt: dagger.PromptState = dag.prompt(input="y").prompt()
        outcome = await prompt.outcome()  # True because input is "y"

        if outcome:
            return dag.container().from_("alpine").with_exec(cmd=["echo", "Deploying..."])
        else:
            return dag.container().from_("alpine").with_exec(cmd=["echo", "Skipping deployment..."])

    @function
    async def Prompt_Terminal(self) -> dagger.Container:
        prompt: dagger.PromptState = dag.prompt(ci=False, msg="Do you want to deploy? (y/n)").prompt()  # Terminal prompt
        outcome = await prompt.outcome()  # Depending on user input (y/n)

        if outcome:
            return dag.container().from_("alpine").with_exec(cmd=["echo", "Deploying..."])
        else:
            return dag.container().from_("alpine").with_exec(cmd=["echo", "Skipping deployment..."])