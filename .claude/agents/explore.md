# Explore Agent

Fast agent for exploring codebases. Use for quick searches, finding files, or answering questions about the codebase.

## When to Use

- Quick file searches by pattern
- Finding where something is defined
- Answering "how does X work?" questions
- General codebase exploration

## Thoroughness Levels

Specify when calling:

- **quick** - Basic searches, first few matches
- **medium** - Moderate exploration, follows some leads
- **very thorough** - Comprehensive analysis across multiple locations

## Example Prompts

```
Quick: find all TypeScript files in src/components
```

```
Medium: how do API endpoints work in this codebase?
```

```
Very thorough: map out all the data fetching patterns used
```

## Best Practices

- Start with quick, escalate if needed
- Be specific about what you're looking for
- Mention thoroughness level explicitly
