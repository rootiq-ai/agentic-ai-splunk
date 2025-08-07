# run_scripts/run_api.sh
#!/bin/bash

echo "Starting Splunk Agentic AI - API Server..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run FastAPI with Uvicorn
python -m uvicorn src.api.main:app --host=${API_HOST:-0.0.0.0} --port=${API_PORT:-8000} --reload
