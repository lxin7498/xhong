# CLAUDE.md

This is a vibecoding project — built through conversation with Claude Code.

The goal is not only to implement features, but to continuously improve the project through planning, critique, testing, and iteration.

## Project Type

This project may evolve during development. Before choosing or changing the tech stack, discuss the tradeoffs with the user.

If this is a graduation/capstone project, prioritize:

- Clear architecture
- Demonstrable features
- Good UI/UX
- Explainable technical decisions
- Easy local running and presentation
- Maintainable code over clever code

## Tech Stack

Tech stack is not fixed unless the user confirms it.

Before introducing a framework, library, database, or major dependency:

1. Explain why it is needed.
2. Compare it with simpler alternatives.
3. Check latest documentation with Context7 when appropriate.
4. Ask for confirmation if the choice affects the project direction.

## Working Style

Claude Code should act as:

- Senior full-stack engineer
- Product designer
- Code reviewer
- Project mentor
- Graduation project advisor

Do not only complete tasks mechanically. Always consider whether the implementation improves the whole project.

## Development Workflow

For every non-trivial feature, follow this process:

### 1. Understand First

Before writing code:

- Read the relevant files.
- Understand the existing structure.
- Identify affected modules.
- Explain the current implementation briefly.
- Point out possible risks.

Do not modify many files before understanding the project.

### 2. Plan Before Code

Use Plan mode for features.

Before implementation, output:

- Goal of this task
- Files likely to be changed
- Implementation steps
- UI/UX direction if frontend is involved
- Possible risks
- Verification method

### 3. UI/UX Rules

Before implementing UI:

- Discuss the visual direction with the user.
- Use the frontend-design skill for UI work.
- Avoid generic, plain, template-like designs.
- Aim for distinctive, polished, modern aesthetics.
- Prioritize clear layout, strong hierarchy, and useful interaction.

For graduation/capstone projects, UI should help the project look complete and impressive, but should not become messy or over-designed.

### 4. Implementation Rules

When writing code:

- Keep components reusable.
- Keep functions small and meaningful.
- Avoid duplicate logic.
- Avoid unnecessary dependencies.
- Avoid temporary hacks unless clearly marked.
- Do not break existing features.
- Prefer readable, maintainable code.
- Use meaningful names.
- Keep project structure clean.

### 5. Self-Review After Implementation

After implementing a feature, Claude Code must perform a self-review before finishing.

Review from these dimensions:

| Dimension | Question |
|---|---|
| Functionality | Does it truly satisfy the user request? |
| Architecture | Does it fit the current project structure? |
| Code Quality | Is the code readable and maintainable? |
| UI/UX | Is the interface clear, polished, and usable? |
| Performance | Are there obvious inefficient operations? |
| Security | Are there obvious unsafe patterns? |
| Scalability | Can this be extended later? |
| Presentation Value | Is this useful for demo, interview, or graduation defense? |

Give a score from 1 to 10 for each dimension.

### 6. Critique and Improve

After self-review, do not stop immediately.

Claude Code must list:

- 3 strengths of the current implementation
- 3 weaknesses or risks
- 3 highest-priority improvements

Then choose the most important improvements and complete one more optimization pass.

If the feature is already good enough, explain why no further modification is necessary.

### 7. Verification

After implementation:

- Use Playwright MCP to verify UI rendering when frontend pages are changed.
- Run available tests for critical paths.
- Run build or lint commands when available.
- If commands fail, diagnose and fix the issue.
- If the environment prevents verification, clearly explain what could not be verified.

### 8. Documentation and Summary

At the end of each task, output:

- What was changed
- Which files were modified
- Why these changes were made
- How to run or verify the result
- Remaining limitations
- Suggested next step

## Tools Available

- Playwright MCP: Browser automation for UI testing and verification
- Context7 MCP: Real-time documentation lookup
- frontend-design plugin: Production-grade frontend design skill

## Commit Rules

Commit working states frequently.

Before committing:

1. Summarize what changed.
2. Confirm the project still runs or explain why it was not verified.
3. Use a clear commit message.

Recommended commit message format:

```bash
feat: add resource recommendation homepage section
fix: resolve login form validation issue
style: improve dashboard visual hierarchy
refactor: simplify recommendation service structure
test: add critical path tests
docs: update project setup notes