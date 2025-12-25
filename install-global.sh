#!/bin/bash
# Install Continuous Claude globally to ~/.claude/
# This enables all features in any project, not just this repo.
#
# Usage: ./install-global.sh
#
# ⚠️  WARNING: This script REPLACES the following directories:
#   ~/.claude/skills/     - Replaced entirely
#   ~/.claude/agents/     - Replaced entirely
#   ~/.claude/rules/      - Replaced entirely
#   ~/.claude/hooks/      - Replaced entirely
#   ~/.claude/scripts/    - Files added/overwritten
#   ~/.claude/settings.json - Replaced (backup created)
#
# ✓ Preserved:
#   ~/.claude/.env        - Not touched if exists
#   ~/.claude/cache/      - Not touched
#   ~/.claude/state/      - Not touched
#
# Safe to run multiple times - settings.json is backed up before overwrite.
# If you have custom skills/agents/rules, copy them to a safe location first.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GLOBAL_DIR="$HOME/.claude"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Installing Continuous Claude to $GLOBAL_DIR..."
echo ""

# Create global dir if needed
mkdir -p "$GLOBAL_DIR"

# Backup existing settings if present
if [ -f "$GLOBAL_DIR/settings.json" ]; then
    cp "$GLOBAL_DIR/settings.json" "$GLOBAL_DIR/settings.json.backup.$TIMESTAMP"
    echo "Backed up existing settings.json"
fi

# Copy directories (overwrite)
echo "Copying skills..."
rm -rf "$GLOBAL_DIR/skills"
cp -r "$SCRIPT_DIR/.claude/skills" "$GLOBAL_DIR/skills"

echo "Copying agents..."
rm -rf "$GLOBAL_DIR/agents"
cp -r "$SCRIPT_DIR/.claude/agents" "$GLOBAL_DIR/agents"

echo "Copying rules..."
rm -rf "$GLOBAL_DIR/rules"
cp -r "$SCRIPT_DIR/.claude/rules" "$GLOBAL_DIR/rules"

echo "Copying hooks..."
rm -rf "$GLOBAL_DIR/hooks"
cp -r "$SCRIPT_DIR/.claude/hooks" "$GLOBAL_DIR/hooks"
# Remove source files (only dist needed for runtime)
rm -rf "$GLOBAL_DIR/hooks/src" "$GLOBAL_DIR/hooks/node_modules" "$GLOBAL_DIR/hooks/*.ts" 2>/dev/null || true

echo "Copying scripts..."
mkdir -p "$GLOBAL_DIR/scripts"
cp "$SCRIPT_DIR/scripts/"*.py "$GLOBAL_DIR/scripts/" 2>/dev/null || true
cp "$SCRIPT_DIR/.claude/scripts/"*.sh "$GLOBAL_DIR/scripts/" 2>/dev/null || true

# Copy settings.json (use project version as base)
echo "Installing settings.json..."
cp "$SCRIPT_DIR/.claude/settings.json" "$GLOBAL_DIR/settings.json"

# Create .env if it doesn't exist
if [ ! -f "$GLOBAL_DIR/.env" ]; then
    echo "Creating .env template..."
    cp "$SCRIPT_DIR/.env.example" "$GLOBAL_DIR/.env"
    echo ""
    echo "IMPORTANT: Edit ~/.claude/.env and add your API keys:"
    echo "  - BRAINTRUST_API_KEY (for session tracing)"
    echo "  - PERPLEXITY_API_KEY (for web search)"
    echo "  - etc."
else
    echo ".env already exists (not overwritten)"
fi

# Create required cache directories
mkdir -p "$GLOBAL_DIR/cache/learnings"
mkdir -p "$GLOBAL_DIR/cache/insights"
mkdir -p "$GLOBAL_DIR/cache/agents"
mkdir -p "$GLOBAL_DIR/state/braintrust_sessions"

echo ""
echo "Installation complete!"
echo ""
echo "Features now available in any project:"
echo "  - Continuity ledger (/continuity_ledger)"
echo "  - Handoffs (/create_handoff, /resume_handoff)"
echo "  - TDD workflow (auto-activates on 'implement', 'fix bug')"
echo "  - Session tracing (if BRAINTRUST_API_KEY set)"
echo "  - All skills and agents"
echo ""
echo "To update later, pull the repo and run this script again."
