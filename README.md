# 🔍 Splunk Agentic AI

A comprehensive application that converts natural language questions to SPL (Search Processing Language) queries using OpenAI and executes them on Splunk. Features both a modern Streamlit UI and comprehensive REST API.

## ✨ Features

- 🤖 **AI-Powered Query Generation**: Convert natural language to SPL using OpenAI GPT-4
- 🔍 **Direct SPL Execution**: Execute raw SPL queries directly  
- 🌐 **REST API**: Complete API with OpenAPI documentation
- 🖥️ **Interactive UI**: Modern Streamlit interface with real-time results
- 📊 **Data Visualization**: Built-in charts and graphs for query results
- 🔐 **Secure Authentication**: Token-based Splunk authentication
- 📝 **Query History**: Track and rerun previous queries
- ⚡ **Performance Monitoring**: Real-time health checks and statistics
- 🧪 **Comprehensive Testing**: Full test suite included

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   FastAPI REST  │    │   Core Engine   │
│                 │    │      API        │    │                 │
│  • Query Input  │    │  • Endpoints    │    │ • QueryProcessor│
│  • Visualizations │  │  • Documentation│    │ • SplunkClient  │
│  • History      │    │  • Validation   │    │ • OpenAIClient  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
    ┌─────────────────────────────┼─────────────────────────────┐
    │                             ▼                             │
    │                   Query Processor                         │
    │                                                           │
    │  ┌─────────────────┐              ┌─────────────────┐     │
    │  │  OpenAI Client  │              │  Splunk Client  │     │
    │  │                 │              │                 │     │
    │  │ • NL → SPL      │              │ • Query Exec    │     │
    │  │ • Query Enhancement │           │ • Results       │     │  
    │  │ • Suggestions   │              │ • Validation    │     │
    │  └─────────────────┘              └─────────────────┘     │
    └─────────────────────────────────────────────────────────────┘
                                 │
                 ┌───────────────┼───────────────┐
                 ▼               ▼               ▼
         ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
         │   OpenAI    │ │   Splunk    │ │ File System │
         │     API     │ │  Instance   │ │   (Logs)    │
         └─────────────┘ └─────────────┘ └─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Splunk Enterprise/Cloud instance
- OpenAI API key
- Git

### 1. Clone Repository

```bash
git clone https://github.com/your-org/splunk-agentic-ai.git
cd splunk-agentic-ai
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Splunk Configuration
SPLUNK_HOST=your-splunk-host.com
SPLUNK_PORT=8089
SPLUNK_USERNAME=admin
SPLUNK_PASSWORD=your-password
# OR use token instead of username/password
SPLUNK_TOKEN=your-splunk-token

# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-key-here

# Optional: Customize ports
API_PORT=8000
STREAMLIT_PORT=8501
```

### 4. Run the Application

Choose your preferred option:

**Option A: Streamlit UI Only**
```bash
chmod +x run_scripts/run_streamlit.sh
./run_scripts/run_streamlit.sh
```
Access at: http://localhost:8501

**Option B: API Server Only**
```bash
chmod +x run_scripts/run_api.sh
./run_scripts/run_api.sh
```
Access at: http://localhost:8000
API Docs: http://localhost:8000/api/v1/docs

**Option C: Both UI and API**
```bash
chmod +x run_scripts/run_both.sh
./run_scripts/run_both.sh
```

## 📖 Usage Examples

### Streamlit UI

1. **Open the UI**: Navigate to `http://localhost:8501`
2. **Ask Questions**: Type natural language questions like:
   - "Show me error logs from the last hour"
   - "What are the top source IPs by traffic volume?"
   - "Find failed login attempts in the last 24 hours"
3. **View Results**: See generated SPL, execution statistics, and visualized data
4. **Explore History**: Review and rerun previous queries

### REST API

#### Natural Language Query
```bash
curl -X POST "http://localhost:8000/api/v1/query/natural" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "Show me failed login attempts in the last hour",
       "max_results": 100
     }'
```

#### Direct SPL Query
```bash
curl -X POST "http://localhost:8000/api/v1/query/spl" \
     -H "Content-Type: application/json" \
     -d '{
       "spl_query": "search index=security action=login result=failure | head 10",
       "max_results": 100
     }'
```

#### Python Example
```python
import requests

# Natural language query
response = requests.post(
    "http://localhost:8000/api/v1/query/natural",
    json={
        "question": "Show me the top 10 users by login count today",
        "max_results": 50
    }
)

result = response.json()
print(f"Generated SPL: {result['spl_query']}")
print(f"Found {result['result_count']} results")

for event in result['results']:
    print(event)
```

## 📚 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/query/natural` | Convert natural language to SPL and execute |
| `POST` | `/api/v1/query/spl` | Execute raw SPL query |
| `POST` | `/api/v1/query/enhance` | Enhance existing SPL query |
| `POST` | `/api/v1/query/suggestions` | Get query suggestions |
| `GET` | `/api/v1/query/health` | Health check |
| `GET` | `/api/v1/query/indexes` | List available indexes |
| `GET` | `/api/v1/query/history` | Get search history |

### Response Format

All endpoints return JSON responses with consistent structure:

```json
{
  "success": true,
  "question": "Show me error logs",
  "spl_query": "search index=main error | head 100",
  "explanation": "Search for error events in the main index",
  "confidence": "high",
  "results": [...],
  "result_count": 42,
  "statistics": {
    "result_count": 42,
    "scan_count": 1000,
    "run_duration": 1.5,
    "search_id": "1234567890.123"
  },
  "processing_time": 2.3
}
```

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Run specific test categories:
```bash
# Test Splunk client
python -m pytest tests/test_splunk_client.py -v

# Test OpenAI client  
python -m pytest tests/test_openai_client.py -v

# Test API endpoints
python -m pytest tests/test_api.py -v
```

## 📁 Project Structure

```
splunk-agentic-ai/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── .gitignore              # Git ignore rules
├── config/
│   └── config.py           # Configuration management
├── src/
│   ├── core/               # Core business logic
│   │   ├── splunk_client.py    # Splunk integration
│   │   ├── openai_client.py    # OpenAI integration  
│   │   └── query_processor.py  # Main orchestrator
│   ├── api/                # REST API
│   │   ├── main.py            # FastAPI application
│   │   ├── routes/            # API route handlers
│   │   └── models/            # Pydantic models
│   ├── ui/                 # User interface
│   │   └── streamlit_app.py   # Streamlit application
│   └── utils/              # Utilities
│       ├── logger.py          # Logging configuration
│       └── validators.py      # Input validation
├── tests/                  # Test suite
│   ├── test_splunk_client.py
│   ├── test_openai_client.py
│   └── test_api.py
└── run_scripts/            # Execution scripts
    ├── run_streamlit.sh
    ├── run_api.sh
    └── run_both.sh
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SPLUNK_HOST` | Splunk server hostname | ✅ | localhost |
| `SPLUNK_PORT` | Splunk server port | ✅ | 8089 |
| `SPLUNK_USERNAME` | Splunk username | ✅* | admin |
| `SPLUNK_PASSWORD` | Splunk password | ✅* | - |
| `SPLUNK_TOKEN` | Splunk auth token | ✅* | - |
| `SPLUNK_SCHEME` | HTTP scheme | ❌ | https |
| `OPENAI_API_KEY` | OpenAI API key | ✅ | - |
| `OPENAI_MODEL` | OpenAI model | ❌ | gpt-4 |
| `LOG_LEVEL` | Logging level | ❌ | INFO |
| `API_HOST` | API bind host | ❌ | 0.0.0.0 |
| `API_PORT` | API port | ❌ | 8000 |
| `STREAMLIT_PORT` | UI port | ❌ | 8501 |

*Either `SPLUNK_TOKEN` or `SPLUNK_USERNAME`/`SPLUNK_PASSWORD` required

### Splunk Setup

1. **Enable REST API**: Ensure Splunk REST API is enabled
2. **Create Service Account**: Recommended to use dedicated service account
3. **Generate Token**: Preferred authentication method
   ```bash
   curl -k -u admin:password https://splunk-host:8089/services/auth/tokens \
        -d name=agentic-ai -d audience=users
   ```
4. **Set Permissions**: Ensure account has search permissions

### OpenAI Setup

1. **Get API Key**: Visit https://platform.openai.com/api-keys
2. **Set Usage Limits**: Configure spending limits
3. **Monitor Usage**: Track API usage and costs

## 🔒 Security Considerations

- **Environment Variables**: Never commit `.env` files
- **API Keys**: Rotate keys regularly
- **Network Security**: Use HTTPS in production
- **Input Validation**: All inputs are validated and sanitized
- **Query Restrictions**: Dangerous SPL commands are blocked
- **Rate Limiting**: Implement rate limiting in production

## 🚀 Production Deployment

### Using Docker (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000 8501

CMD ["./run_scripts/run_both.sh"]
```

### Using systemd

Create service files:

```ini
# /etc/systemd/system/splunk-agentic-api.service
[Unit]
Description=Splunk Agentic AI API
After=network.target

[Service]
Type=exec
User=splunk-ai
WorkingDirectory=/opt/splunk-agentic-ai
ExecStart=/opt/splunk-agentic-ai/run_scripts/run_api.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

### Environment-Specific Configuration

**Development**:
```bash
DEBUG=True
LOG_LEVEL=DEBUG
```

**Production**:
```bash
DEBUG=False  
LOG_LEVEL=WARNING
API_HOST=127.0.0.1  # Restrict to localhost
```

## 🛠️ Development

### Adding New Features

1. **Core Logic**: Add to `src/core/`
2. **API Endpoints**: Add to `src/api/routes/`
3. **UI Components**: Add to `src/ui/`
4. **Tests**: Add to `tests/`

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings
- Include unit tests

### Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## 📊 Monitoring

### Logs

Logs are written to stdout in structured format:
```
2024-08-07 10:30:15 - src.core.query_processor - INFO - Processing natural language query: Show me errors
2024-08-07 10:30:16 - src.core.openai_client - INFO - Generated SPL: search index=main error | head 100
2024-08-07 10:30:17 - src.core.splunk_client - INFO - Search completed. Results: 42, Duration: 1.5s
```

### Health Monitoring

Monitor the `/api/v1/query/health` endpoint:
```bash
curl http://localhost:8000/api/v1/query/health
```

### Performance Metrics

- Query processing time
- Splunk search duration  
- Result counts
- Error rates

## ❗ Troubleshooting

### Common Issues

**Connection to Splunk fails**:
- Verify host/port settings
- Check authentication credentials
- Ensure Splunk REST API is enabled
- Test with curl: `curl -k https://splunk-host:8089/services/auth/login`

**OpenAI API errors**:
- Verify API key is correct
- Check quota/billing status
- Monitor rate limits

**Import errors**:
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check Python path: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`

**Performance issues**:
- Reduce `max_results` parameter
- Add more specific search terms
- Use time-based filtering
- Check Splunk cluster performance

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
export DEBUG=True
```

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Support

- **Documentation**: Check this README and API docs
- **Issues**: Report bugs via GitHub Issues  
- **Questions**: Use GitHub Discussions
- **Security**: Report security issues privately

---

**Happy Splunking! 🔍✨**
