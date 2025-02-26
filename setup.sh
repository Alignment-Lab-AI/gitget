#!/bin/bash
# install_gitget.sh
# This script moves gitget.py from the current directory to a permanent location,
# renames it to "gitget", and sets up a permanent alias in the appropriate shell config.
#
# Usage:
#   ./install_gitget.sh

# Determine OS type
OS=$(uname)
if [[ "$OS" == "Linux" ]]; then
    DEST_DIR="$HOME/.local/bin"
    RC_FILE="$HOME/.bashrc"
elif [[ "$OS" == "Darwin" ]]; then
    DEST_DIR="$HOME/bin"
    RC_FILE="$HOME/.zshrc"
else
    echo "Unsupported OS: $OS"
    exit 1
fi

# Create destination directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Verify that gitget.py exists in the current directory
if [ ! -f "./gitget.py" ]; then
    echo "Error: gitget.py not found in the current directory."
    exit 1
fi

# Move gitget.py to the destination directory and rename it to "gitget"
mv "./gitget.py" "$DEST_DIR/gitget" || { echo "Failed to move gitget.py"; exit 1; }

# Ensure the file is executable
chmod +x "$DEST_DIR/gitget"

# Define the alias command (using the full path)
ALIAS_CMD="alias gitget=\"$DEST_DIR/gitget\""

# Add the alias to the appropriate shell configuration file if not already present
if ! grep -Fxq "$ALIAS_CMD" "$RC_FILE"; then
    echo "" >> "$RC_FILE"
    echo "# Alias for gitget command" >> "$RC_FILE"
    echo "$ALIAS_CMD" >> "$RC_FILE"
    echo "Alias added to $RC_FILE"
else
    echo "Alias already exists in $RC_FILE"
fi

echo "Installation complete."
echo "Please restart your terminal or run 'source $RC_FILE' to activate the alias."
