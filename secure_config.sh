#!/bin/bash
# Script to secure configuration files with proper permissions

# Set restrictive permissions on config file
CONFIG_FILE="$HOME/.pod_automation_config.json"

if [ -f "$CONFIG_FILE" ]; then
    echo "Setting secure permissions (600) on $CONFIG_FILE"
    chmod 600 "$CONFIG_FILE"
    echo "Done. File is now only readable by the owner."
else
    echo "Config file $CONFIG_FILE not found. No action taken."
fi

# Remind about .env file
if [ -f ".env" ]; then
    echo "Setting secure permissions (600) on .env file"
    chmod 600 ".env"
    echo "Done. .env file is now only readable by the owner."
else
    echo ".env file not found. Remember to create one from .env.example"
    echo "and set secure permissions with: chmod 600 .env"
fi

echo ""
echo "Security reminder:"
echo "- Never commit .env or config files to source control"
echo "- Use environment variables for secrets in production"
echo "- Regularly rotate API keys and secrets"
