#!/bin/bash
set -e

# Script purpose: install the JupyterLab extension for Lean 4

# get script parent directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_ROOT=$SCRIPT_DIR/..
EXT_DIR=$PROJECT_ROOT/ext
VENV_DIR=$PROJECT_ROOT/.venv

# Create and activate virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Check if nvm is installed, install if not present
if [ ! -d "${NVM_DIR:-$HOME/.nvm}" ]; then
  echo "nvm not found. Installing nvm..."
  export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
  # Download and run the install script
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
fi

# Load nvm
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" # This loads nvm

# Verify nvm is available
if ! command -v nvm &>/dev/null; then
  echo "Failed to load nvm. Please check your installation."
  exit 1
fi

# Install and use Node.js LTS version
nvm install --lts
nvm use --lts

# Navigate to extension directory
cd "$EXT_DIR"

# Install the extension
echo "Installing the JupyterLab extension..."
jlpm install
jlpm build

# Install in development mode
echo "Installing in development mode..."
"$VENV_DIR/bin/pip" install -e .
"$VENV_DIR/bin/jupyter" labextension develop . --overwrite

# Verify installation
jupyter labextension list

echo "JupyterLab extension installation completed successfully"
