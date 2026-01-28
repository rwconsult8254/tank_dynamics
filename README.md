# Tank Dynamics Simulator

A real-time tank level control simulator with a SCADA-style interface. The system models a tank with variable inlet flow and PID-controlled outlet valve, allowing operators to experiment with control parameters and observe process dynamics.

## Architecture

- **C++ Simulation Core**: High-performance physics engine using GSL and Eigen
- **Python Bindings**: pybind11 interface for Python integration
- **FastAPI Backend**: Real-time WebSocket server (1 Hz updates)
- **Next.js Frontend**: Modern web-based SCADA interface

## Developer Setup

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt-get install cmake libgsl-dev build-essential

# Arch Linux
sudo pacman -S cmake gsl base-devel

# macOS
brew install cmake gsl
```

### Building the Project

```bash
# Configure build
cmake -B build -S .

# Build
cmake --build build

# Run tests
ctest --test-dir build --output-on-failure
```

### IDE/Editor Integration (clangd)

For proper IDE integration with clangd (VSCode, neovim, etc.), create a symlink to the generated `compile_commands.json`:

```bash
# From project root
ln -sf build/compile_commands.json compile_commands.json
```

This enables:
- Accurate code completion
- Go-to-definition across the project
- Real-time error highlighting
- Automatic include path resolution

**Note:** The build system automatically generates `compile_commands.json` in the `build/` directory via `CMAKE_EXPORT_COMPILE_COMMANDS`. The symlink makes it discoverable by clangd at the project root.

### Git Ignore

Add to `.gitignore`:
```
build/
compile_commands.json
```

## Quick Start

1. Build the C++ library (see above)
2. Run the test suite to verify installation
3. (Future) Install Python bindings: `pip install -e .`
4. (Future) Start the API server: `python -m api.main`
5. (Future) Start the frontend: `cd frontend && npm run dev`

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
