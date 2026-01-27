# Hybrid AI Coding Project Template

A template for multi-role AI-assisted software development using Claude models and local LLMs.

## Overview

This template implements a proven workflow that optimizes AI costs while maintaining code quality:

- **Expensive models** (Opus) handle high-value planning
- **Mid-tier models** (Sonnet) handle task breakdown and code review
- **Cheap/free models** (Haiku, local LLMs) handle implementation and documentation

## Quick Start

1. Clone or copy this template to your project directory
2. Edit `docs/specs.md` with your project requirements
3. Follow the workflow in `docs/workflow.md`

```bash
# Using the setup script
./scripts/new-project.sh my-project-name

# Or manually
cp -r hybrid-ai-template/ my-new-project/
cd my-new-project
git init
```

## Workflow Roles

| Role | Model | Responsibility | Deliverable |
|------|-------|----------------|-------------|
| Architect | Claude Opus | Strategic planning | `docs/plan.md` |
| Senior Engineer | Claude Sonnet | Task breakdown | `docs/next.md` |
| Engineer | Local LLM + Human | Implementation | Code |
| Code Reviewer | Claude Sonnet | Quality assurance | `docs/feedback.md` |
| Documentation Writer | Claude Haiku | User/dev docs | README, guides |
| Docstring Writer | Local LLM | Code documentation | Inline docstrings |

## Model Selection Guide

| Task Type | Recommended Model | Notes |
|-----------|-------------------|-------|
| Architecture & Planning | Claude Opus | Broad context needed |
| Task Breakdown | Claude Sonnet | Balance of capability/cost |
| Backend Implementation | Local LLM (14B+) | Well-defined patterns |
| Frontend (React/Vue/etc) | Claude Haiku | Ecosystem complexity |
| Documentation | Claude Haiku | Excellent at structured writing |
| Code Review | Claude Sonnet | Nuanced understanding |
| Docstrings | Local LLM | Mechanical, defined task |
| Shell/Terminal Commands | Human or Claude | Local LLM unreliable |

## Directory Structure

```
project/
├── CLAUDE.md              # Role definitions and rules
├── prompts/
│   ├── architect.md
│   ├── senior-engineer.md
│   ├── engineer.md
│   ├── code-reviewer.md
│   ├── documentation-writer.md
│   └── docstring-writer.md
├── docs/
│   ├── specs.md           # Your project specification
│   ├── plan.md            # Created by Architect
│   ├── next.md            # Created by Senior Engineer
│   ├── workflow.md        # Step-by-step guide
│   └── feedback.md        # Created by Code Reviewer
├── src/                   # Your source code
├── tests/                 # Your tests
└── scripts/
    └── new-project.sh
```

## Key Principles

1. **Git from day one** - Commit after each task for context and rollback
2. **Hard prompt boundaries** - Forbidden actions, not guidelines
3. **Escalation paths** - Know when to switch from local LLM to Claude
4. **Human oversight** - AI judgment isn't reliable for all decisions

## Escalation Triggers

Switch from local LLM to Haiku/Sonnet when:
- Task involves unfamiliar framework (React, Vue, complex libraries)
- Model produces repeated errors on same task
- Output doesn't match specification after 2 attempts
- Task requires terminal/shell commands
- Complex refactoring across multiple files

## License

This template is provided as-is for personal and commercial use.
