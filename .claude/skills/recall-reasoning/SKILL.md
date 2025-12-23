---
description: Search past reasoning for relevant decisions and approaches
---

# Recall Past Reasoning

Search through previous development sessions to find relevant decisions, approaches that worked, and approaches that failed.

## When to use

- Starting a new feature that's similar to past work
- Investigating why something was done a certain way
- Looking for patterns that worked before
- Debugging an issue that might have been encountered previously

## Usage

```bash
bash .claude/scripts/search-reasoning.sh "<query>"
```

## Examples

```bash
# Search for rate limiting related reasoning
bash .claude/scripts/search-reasoning.sh "rate limiting"

# Search for authentication decisions
bash .claude/scripts/search-reasoning.sh "authentication"

# Search for build failures
bash .claude/scripts/search-reasoning.sh "build fail"

# Search for specific error types
bash .claude/scripts/search-reasoning.sh "TypeError"
```

## What gets searched

The search looks through reasoning files which contain:
- **Failed build attempts** - Commands that failed and their error output
- **Successful builds** - What finally worked after failures
- **Commit context** - What was being worked on when attempts were made
- **Branch information** - Which feature branch the work was done on

## How to interpret results

- `build_fail` entries show approaches that didn't work
- `build_pass` shows what finally succeeded
- The context helps understand why certain decisions were made
- Multiple failures before success indicate the problem was non-trivial

## How reasoning is captured

1. PostToolUse hook captures build/test command results
2. Results stored in `.git/claude/branches/<branch>/attempts.jsonl`
3. When `/commit` runs, it generates `.git/claude/commits/<hash>/reasoning.md`
4. This skill searches across all reasoning files

## No results?

If no reasoning files are found:
- Reasoning tracking may not have been enabled for older commits
- Try running builds with `/commit` to start capturing reasoning
- Check if `.git/claude/` directory exists
