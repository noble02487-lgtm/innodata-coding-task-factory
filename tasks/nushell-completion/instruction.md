# Add Nushell shell completion support to Click

The repository at `/app` is the Click command-line library (Python), checked out at a fixed commit. Click already supports shell completion for bash, zsh, fish and PowerShell (see `click/shell_completion.py`). Add support for the **Nushell** shell in the same style.

## Required API

- A new class `NushellComplete` in `click.shell_completion`, subclassing `ShellComplete`, with `name = "nushell"`, registered so that `get_completion_class("nushell")` returns it (and the usual `_CLI_COMPLETE=nushell_source` / `nushell_complete` activation works through the existing `shell_complete` machinery).

## Behavior

- `source()` returns a Nushell script that defines a custom completer named `nu-complete <prog_name>` and an `extern` declaration for the program using it. The script must set the completion environment variable to `nushell_complete` when calling the program, and must pass the current command line through the `COMP_WORDS` / `COMP_CWORD` environment variables (full line string, and index of the word being completed).
- Completion arguments are read from `COMP_WORDS` / `COMP_CWORD` exactly like the bash implementation: previous words are the args, the word at `COMP_CWORD` is the incomplete word.
- Each completion item is formatted as **three lines** — item type, item value, help text — with the literal `_` as the help when the item has no help text. Newlines and carriage returns inside help text are collapsed to spaces so the three-line framing stays intact.

## Example

```console
$ _CLI_COMPLETE=nushell_source mycli   # prints the Nushell script
$ _CLI_COMPLETE=nushell_complete COMP_WORDS="mycli " COMP_CWORD=1 mycli
plain
alpha
First command.
plain
beta
Second command.
```

All pre-existing tests in the repository's `tests/` directory must continue to pass.
