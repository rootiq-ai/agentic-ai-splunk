# run_scripts/run_both.sh
#!/bin/bash

echo "Starting Splunk Agentic AI - Both API and UI..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start API server in background
echo "Starting API server on port ${API_PORT:-8000}..."
python -m uvicorn src.api.main:app --host=${API_HOST:-0.0.0.0} --port=${API_PORT:-8000} &
API_PID=$!

# Wait a moment for API to start
sleep 3

# Start Streamlit on different port
echo "Starting Streamlit UI on port ${STREAMLIT_PORT:-8501}..."
streamlit run src/ui/streamlit_app.py --server.port=${STREAMLIT_PORT:-8501} --server.address=0.0.0.0 &
STREAMLIT_PID=$!

echo "Both services started!"
echo "API: http://localhost:${API_PORT:-8000}"
echo "UI: http://localhost:${STREAMLIT_PORT:-8501}"
echo "API Docs: http://localhost:${API_PORT:-8000}/api/v1/docs"

# Function to cleanup processes
cleanup() {
    echo "Shutting down services..."
    kill $API_PID 2>/dev/null
    kill $STREAMLIT_PID 2>/dev/null
    exit
}

# Trap Ctrl+C and other termination signals
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
