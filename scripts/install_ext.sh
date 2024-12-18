#!/bin/bash
set -e

# Script purpose: install the JupyterLab extension for Lean 4

# get script parent directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
PROJECT_ROOT=$SCRIPT_DIR/..
EXT_DIR=$PROJECT_ROOT/ext
VENV_DIR=$PROJECT_ROOT/.venv

# Only create/use venv if not in CI
if [ -z "$CI" ]; then
  if [ ! -d "$VENV_DIR" ]; then
    echo "Creating new virtual environment..."
    python3 -m venv "$VENV_DIR"
  else
    echo "Using existing virtual environment..."
  fi

  echo "Activating virtual environment..."
  source "$VENV_DIR/bin/activate"
  PIP="$VENV_DIR/bin/pip"
  PYTHON="$VENV_DIR/bin/python"
else
  PIP="pip"
  PYTHON="python"
fi

# Update pip in virtual environment
echo "Updating pip..."
"$PYTHON" -m pip install --upgrade pip

# Check if node is installed and meets minimum version
if ! command -v node >/dev/null 2>&1; then
  echo "Node.js not found. Installing via nvm..."
  install_nvm=true
else
  node_version=$(node -v | cut -d'v' -f2)
  required_version="22.0.0"
  if [ "$(printf '%s\n' "$required_version" "$node_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "Node.js version $node_version is sufficient"
    install_nvm=false
  else
    echo "Node.js version $node_version is below required version $required_version. Installing via nvm..."
    install_nvm=true
  fi
fi

if [ "$install_nvm" = true ]; then
  # Install nvm if not present
  if ! command -v nvm >/dev/null 2>&1; then
    echo "Installing nvm..."
    export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
  fi

  # Load nvm
  export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
  [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

  # Install and use Node.js version 22
  nvm install 22
  nvm use 22
fi

# Install required Python packages
echo "Installing Python dependencies..."
"$PIP" install ipykernel jupyterlab jupyter_packaging

# Navigate to extension directory
cd "$EXT_DIR"

# Install the extension
echo "Installing the JupyterLab extension..."
jlpm install
jlpm build

# # Create kernel for this virtual environment
# echo "Creating kernel..."
# "$VENV_DIR/bin/python" -m ipykernel install

# Install in development or production mode
if [ -n "$L4J_DEV" ]; then
  echo "Installing in development mode..."
  "$PIP" install -e .
  jupyter-labextension develop . --overwrite
else
  echo "Installing in production mode..."
  "$PIP" install .
  jupyter-labextension install .
fi

# Verify installations
echo "Verifying kernel installation..."
jupyter kernelspec list
echo "Verifying extension installation..."
jupyter-labextension list

echo "JupyterLab extension installation completed successfully"
