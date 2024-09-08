"""Example of a Prompt module"""

import dagger
from dagger import dag, function, object_type


@object_type
class Examples:
    """Examples of prompts"""

    @function
    async def prompt_choices(self) -> str:
        result = dag.prompt().with_choices(["y", "n"]).execute() # choices
        outcome = await result.outcome()  # true or false based on user input
        input = await result.input()  # the user input
        return f"Outcome: {outcome}, Input: {input}"

    @function
    async def prompt_input(self) -> str:
        prompt = (dag.prompt()
                  .with_msg("Do you want to deploy? Enter 'Deploy' to continue") # custom message
                  .with_input("Deploy") # input from ci pipeline
                  .with_match("Deploy") # regex match of user input
                  .with_ci(True) # ci mode, disables terminal prompt
                  .with_input("y").execute())

        outcome = await prompt.outcome() # true or false based on user input
        input = await prompt.input() # the user input
        return f"Outcome: {outcome}, Input: {input}"
