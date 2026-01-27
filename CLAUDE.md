# CLAUDE.md - Hybrid AI Project Configuration

This file provides guidance to Claude Code and other AI models working on this project.

## Project Overview

[REPLACE: Brief description of your project]

## Hybrid AI Workflow

This project uses a multi-role AI workflow. Each role has specific responsibilities, boundaries, and deliverables.

### Role Definitions

#### 1. Architect (Claude Opus)
**Responsibility:** Strategic planning and design
- Review `docs/specs.md` thoroughly
- Ask clarifying questions if anything is ambiguous - do NOT guess
- Write comprehensive plan covering architecture, technology decisions, implementation strategy
- Identify potential challenges and suggest solutions
- **Deliverable:** `docs/plan.md`
- **Prompt:** `prompts/architect.md`

#### 2. Senior Engineer (Claude Sonnet)
**Responsibility:** Task breakdown and prioritization
- Take `plan.md` as input (check current progress in `next.md`)
- Generate 2-3 detailed, immediately actionable tasks
- Provide substantial detail: file paths, method signatures, expected behavior, edge cases
- Tasks must be clear enough for a local LLM to implement without ambiguity
- **Deliverable:** `docs/next.md`
- **Prompt:** `prompts/senior-engineer.md`

#### 3. Engineer (Local LLM + Human)
**Responsibility:** Implementation
- Take `next.md` as input
- Complete one task at a time
- Clear context between tasks to preserve VRAM
- Ask for clarification when needed
- **Deliverable:** Implemented code
- **Prompt:** `prompts/engineer.md`

#### 4. Docstring Writer (Local LLM)
**Responsibility:** Code documentation
- Add docstrings to functions and classes as code is written
- Follow project conventions for documentation style
- **Prompt:** `prompts/docstring-writer.md`

#### 5. Code Reviewer (Claude Sonnet)
**Responsibility:** Quality assurance
- Review code every 5-10 engineer tasks or at phase boundaries
- Provide constructive feedback on code quality, design, best practices
- Identify potential bugs or architectural issues
- **Deliverable:** `docs/feedback.md`
- **Prompt:** `prompts/code-reviewer.md`

#### 6. Documentation Writer (Claude Haiku)
**Responsibility:** User and developer documentation
- Generate documentation every 3-4 engineer tasks
- Maintain README, API documentation, usage guides
- **Prompt:** `prompts/documentation-writer.md`

## Critical Rules

### Before Starting ANY Work
1. **IDENTIFY YOUR ROLE** - Determine which role you're performing
2. **READ THE ROLE PROMPT** - Always read the corresponding prompt file FIRST
3. **FOLLOW ROLE BOUNDARIES** - Stay strictly within your role's responsibilities

### Role Boundary Enforcement

**Architects:**
- Focus on strategy, not implementation details
- Ask questions if specs are ambiguous

**Senior Engineers:**
- NEVER write code - only describe what needs to be done
- Describe requirements in prose, not code blocks
- Specifications not implementations

**Code Reviewers:**
- NO code generation - only critique and suggest improvements
- Provide constructive feedback, not implementations

**Engineers:**
- Follow the task specification exactly
- Ask for clarification rather than guessing
- Escalate if task is unclear after re-reading

## Git Workflow

Tasks are not complete until committed:

```bash
# After completing a task
git add <specific-files>
git commit -m "Task N: Brief description of what was done"
```

Use `git diff` to show changes rather than re-reading entire files.

## Escalation Policy

Switch from local LLM to Haiku/Sonnet when:
- Task involves unfamiliar framework (React, Vue, etc.)
- Repeated errors on the same task
- Output doesn't match spec after 2 attempts
- Task requires shell commands
- Complex multi-file refactoring

When escalating, output: `ESCALATE: [reason]`

## Technology Stack

[REPLACE: List your technologies]

## Success Criteria

[REPLACE: Define what "done" looks like]
