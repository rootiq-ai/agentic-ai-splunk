# run_scripts/run_streamlit.sh
#!/bin/bash

echo "Starting Splunk Agentic AI - Streamlit UI..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run Streamlit
streamlit run src/ui/streamlit_app.py --server.port=${STREAMLIT_PORT:-8501} --server.address=0.0.0.0
