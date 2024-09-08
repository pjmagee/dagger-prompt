// A generated module for Examples functions
//
// This module has been generated via dagger init and serves as a reference to
// basic module structure as you get started with Dagger.
//
// Two functions have been pre-created. You can modify, delete, or add to them,
// as needed. They demonstrate usage of arguments and return types using simple
// echo and grep commands. The functions can be called from the dagger CLI or
// from one of the SDKs.
//
// The first line in this comment block is a short description line and the
// rest is a long description with more detail on the module's purpose or usage,
// if appropriate. All modules should have a short description.

package main

import (
	"context"
	"fmt"
	"strconv"
)

type Examples struct{}

func (m *Examples) Prompt_Choice() (string, error) {

	result := dag.Prompt().
		WithChoices([]string{"Option 1", "Option 2", "Option 3"}).
		WithMsg("Select an option").
		WithInput("Option 2").
		WithCi(false).
		Execute()

	outcome, _ := result.Outcome(context.Background())
	input, _ := result.Input(context.Background())

	return dag.Container().
		From("alpine:latest").
		WithExec([]string{"echo", fmt.Sprintf("Outcome: %s, Choice: %s", strconv.FormatBool(outcome), input)}).
		Stdout(context.Background())
}

func (m *Examples) Prompt_Input() (string, error) {

	result := dag.Prompt().
		WithMsg("Do you want to continue? (y/n)").
		WithInput("yes").
		WithMatch("y").
		WithCi(false).
		Execute()

	outcome, _ := result.Outcome(context.Background())
	input, _ := result.Input(context.Background())

	return dag.Container().
		From("alpine:latest").
		WithExec([]string{"echo", fmt.Sprintf("Outcome: %s, Choice: %s", strconv.FormatBool(outcome), input)}).
		Stdout(context.Background())

}
