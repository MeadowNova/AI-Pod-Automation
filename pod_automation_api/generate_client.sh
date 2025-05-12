#!/bin/bash

# This script generates a TypeScript client for the API
# It requires openapi-typescript-codegen to be installed
# npm install -g openapi-typescript-codegen

# Create the output directory if it doesn't exist
mkdir -p ../pod_automation_frontend/src/api

# Generate the client
npx openapi-typescript-codegen --input openapi.yaml --output ../pod_automation_frontend/src/api --client axios

echo "TypeScript client generated in ../pod_automation_frontend/src/api"
