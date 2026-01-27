#!/bin/bash

# new-project.sh - Initialize a new hybrid AI coding project
#
# Usage: ./new-project.sh <project-name> [destination-dir]
#
# Examples:
#   ./new-project.sh my-api
#   ./new-project.sh my-api ~/projects/

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory (where template lives)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")"

# Parse arguments
PROJECT_NAME="${1:-}"
DEST_DIR="${2:-.}"

if [ -z "$PROJECT_NAME" ]; then
    echo -e "${RED}Error: Project name required${NC}"
    echo "Usage: $0 <project-name> [destination-dir]"
    exit 1
fi

# Validate project name (alphanumeric, hyphens, underscores only)
if [[ ! "$PROJECT_NAME" =~ ^[a-zA-Z][a-zA-Z0-9_-]*$ ]]; then
    echo -e "${RED}Error: Invalid project name${NC}"
    echo "Project name must start with a letter and contain only letters, numbers, hyphens, and underscores"
    exit 1
fi

# Set up paths
PROJECT_PATH="$DEST_DIR/$PROJECT_NAME"

# Check if project directory already exists
if [ -d "$PROJECT_PATH" ]; then
    echo -e "${RED}Error: Directory already exists: $PROJECT_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}Creating new hybrid AI project: $PROJECT_NAME${NC}"

# Create project directory
mkdir -p "$PROJECT_PATH"

# Copy template files (excluding the scripts directory itself to avoid recursion issues)
echo "Copying template files..."
cp -r "$TEMPLATE_DIR/CLAUDE.md" "$PROJECT_PATH/"
cp -r "$TEMPLATE_DIR/README.md" "$PROJECT_PATH/"
cp -r "$TEMPLATE_DIR/.gitignore" "$PROJECT_PATH/"
cp -r "$TEMPLATE_DIR/prompts" "$PROJECT_PATH/"
cp -r "$TEMPLATE_DIR/docs" "$PROJECT_PATH/"
mkdir -p "$PROJECT_PATH/scripts"
cp "$TEMPLATE_DIR/scripts/new-project.sh" "$PROJECT_PATH/scripts/"

# Create standard directories
echo "Creating project structure..."
mkdir -p "$PROJECT_PATH/src"
mkdir -p "$PROJECT_PATH/tests"

# Rename specs template to specs.md
if [ -f "$PROJECT_PATH/docs/specs-template.md" ]; then
    mv "$PROJECT_PATH/docs/specs-template.md" "$PROJECT_PATH/docs/specs.md"
fi

# Create empty files for workflow outputs
touch "$PROJECT_PATH/docs/plan.md"
touch "$PROJECT_PATH/docs/next.md"
touch "$PROJECT_PATH/docs/feedback.md"

# Update README with project name
sed -i "s/Hybrid AI Coding Project Template/$PROJECT_NAME/g" "$PROJECT_PATH/README.md" 2>/dev/null || \
    sed -i '' "s/Hybrid AI Coding Project Template/$PROJECT_NAME/g" "$PROJECT_PATH/README.md"

# Update CLAUDE.md placeholder
sed -i "s/\[REPLACE: Brief description of your project\]/$PROJECT_NAME - A hybrid AI coding project/g" "$PROJECT_PATH/CLAUDE.md" 2>/dev/null || \
    sed -i '' "s/\[REPLACE: Brief description of your project\]/$PROJECT_NAME - A hybrid AI coding project/g" "$PROJECT_PATH/CLAUDE.md"

# Initialize git repository
echo "Initializing git repository..."
cd "$PROJECT_PATH"
git init -q

# Make initial commit
git add .
git commit -q -m "Initial project setup from hybrid-ai-template

Project: $PROJECT_NAME
Created: $(date +%Y-%m-%d)

Template includes:
- Role prompts for Architect, Senior Engineer, Engineer, Code Reviewer, Documentation Writer
- Workflow documentation
- Git workflow guide
- Specification template"

echo ""
echo -e "${GREEN}Project created successfully!${NC}"
echo ""
echo "Project location: $PROJECT_PATH"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. cd $PROJECT_PATH"
echo "2. Edit docs/specs.md with your project requirements"
echo "3. Read docs/workflow.md for the full process"
echo "4. Start with the Architect role (Claude Opus)"
echo ""
echo "Quick reference:"
echo "  - Prompts:     prompts/"
echo "  - Workflow:    docs/workflow.md"
echo "  - Git guide:   docs/git-workflow.md"
echo "  - Spec:        docs/specs.md (edit this first)"
