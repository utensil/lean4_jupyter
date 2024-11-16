#!/bin/bash
set -e

# Script purpose: install the JupyterLab extension for Lean 4

# get script parent directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_ROOT=$SCRIPT_DIR/..
EXT_DIR=$PROJECT_ROOT/ext

# Check if nvm is installed, install if not present
if [ ! -d "$HOME/.nvm" ]; then
    echo "nvm not found. Installing nvm..."
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    
    # Load nvm
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
else
    # Load existing nvm
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
fi

# Install and use Node.js LTS version
nvm install --lts
nvm use --lts

# Navigate to extension directory
cd "$EXT_DIR"

# Build and install the extension
echo "Building and installing the JupyterLab extension..."
jlpm
jlpm build
pip install -e "."
jupyter labextension develop . --overwrite

echo "JupyterLab extension installation completed"
