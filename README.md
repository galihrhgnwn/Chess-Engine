# Stockfish 18 REST API

A production-ready REST API for interacting with the **Stockfish 18 chess engine**. This API provides endpoints for chess position analysis, best move calculation, and FEN validation through a simple HTTP interface.

## Features

- **Best Move Analysis**: Get the best move for any chess position with configurable search depth
- **Position Evaluation**: Evaluate chess positions with detailed analysis metrics
- **FEN Validation**: Validate chess positions in FEN notation
- **Real-time Analysis**: Stream analysis data with configurable time/depth limits
- **CORS Support**: Full cross-origin resource sharing for web applications
- **Interactive Documentation**: Auto-generated Swagger UI and ReDoc documentation
- **Docker Support**: Ready-to-deploy containerized application
- **Multi-platform Deployment**: Configured for Railway, Render, and Heroku

## Quick Start

### Prerequisites

- Python 3.11+
- Stockfish 18 chess engine
- Docker (optional, for containerized deployment)

### Local Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/galihrhgnwn/Chess-Engine.git
   cd Chess-Engine
   ```

2. **Install Stockfish** (Ubuntu/Debian):
   ```bash
   sudo apt-get install stockfish
   ```

   For other systems, download from [stockfishchess.org](https://stockfishchess.org/download/)

3. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env if needed (optional - defaults work for most setups)
   ```

6. **Run the API**:
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

### Docker Deployment

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **Or build and run manually**:
   ```bash
   docker build -t stockfish-api .
   docker run -p 8000:8000 stockfish-api
   ```

## API Documentation

The API is fully documented with interactive Swagger UI and ReDoc. Once running, access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI Schema**: `http://localhost:8000/openapi.json`

### Core Endpoints

#### 1. Health Check

**GET** `/health`

Check API and engine status.

**Response**:
```json
{
  "status": "healthy",
  "engine_ready": true,
  "version": "1.0.0"
}
```

#### 2. Get Best Move

**POST** `/api/best-move`

Calculate the best move for a given position.

**Request Body**:
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "depth": 20,
  "movetime": null
}
```

**Parameters**:
- `fen` (string, required): Chess position in FEN notation
- `depth` (integer, optional): Search depth from 1 to 32 (default: 20)
- `movetime` (integer, optional): Time limit in milliseconds (overrides depth if set)

**Response**:
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "best_move": "e2e4",
  "info": {
    "depth": 20,
    "seldepth": 25,
    "score": {
      "type": "cp",
      "value": 35
    },
    "nodes": 45234567,
    "nps": 2261728,
    "time": 20000,
    "pv": ["e2e4", "c7c5", "g1f3", "d7d6", "d2d4", "c5d4"]
  }
}
```

**Response Fields**:
- `best_move`: The best move in UCI notation (e.g., "e2e4")
- `info.depth`: Search depth achieved
- `info.score.type`: Score type ("cp" for centipawns, "mate" for checkmate)
- `info.score.value`: Score value (positive favors white, negative favors black)
- `info.nodes`: Total nodes evaluated
- `info.nps`: Nodes per second (evaluation speed)
- `info.pv`: Principal variation (best line of play)

#### 3. Evaluate Position

**POST** `/api/evaluate`

Get comprehensive evaluation for a position.

**Request Body**:
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "depth": 20
}
```

**Response**:
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "best_move": "e2e4",
  "evaluation": {
    "type": "cp",
    "value": 35
  },
  "depth": 20,
  "nodes": 45234567
}
```

#### 4. Validate FEN

**GET** `/api/validate-fen?fen=<fen_string>`

Validate a FEN string.

**Query Parameters**:
- `fen` (string, required): FEN string to validate

**Response**:
```json
{
  "valid": true,
  "message": "Valid FEN",
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
}
```

#### 5. Get Starting Position

**GET** `/api/starting-position`

Get the standard chess starting position.

**Response**:
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "description": "Standard chess starting position"
}
```

## Usage Examples

### JavaScript/TypeScript

```javascript
// Analyze starting position
const response = await fetch('http://localhost:8000/api/best-move', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    fen: 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    depth: 20
  })
});

const data = await response.json();
console.log(`Best move: ${data.best_move}`);
console.log(`Evaluation: ${data.info.score.value} centipawns`);
```

### Python

```python
import requests

url = 'http://localhost:8000/api/best-move'
payload = {
    'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    'depth': 20
}

response = requests.post(url, json=payload)
data = response.json()
print(f"Best move: {data['best_move']}")
print(f"Evaluation: {data['info']['score']['value']} centipawns")
```

### cURL

```bash
curl -X POST http://localhost:8000/api/best-move \
  -H "Content-Type: application/json" \
  -d '{
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "depth": 20
  }'
```

## Configuration

Configure the API using environment variables in `.env`:

```env
# Stockfish Configuration
STOCKFISH_PATH=/usr/games/stockfish          # Path to Stockfish binary
STOCKFISH_THREADS=4                          # Number of CPU threads to use
STOCKFISH_MEMORY=512                         # Hash table size in MB

# API Configuration
API_HOST=0.0.0.0                             # Server host
API_PORT=8000                                # Server port
API_WORKERS=4                                # Number of worker processes

# Environment
ENVIRONMENT=development                      # development or production
```

## Deployment

### Generic Python Hosting

For any Python hosting provider (VPS, shared hosting, cloud servers):

1. **Upload Files**
   - Clone or upload all repository files
   - Ensure `main.py`, `requirements.txt`, and `.env.example` are present

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   sudo apt-get install stockfish  # For Linux
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the API**
   ```bash
   python main.py
   ```

5. **Access the API**
   - Swagger UI: `http://your-host:8000/docs`
   - API: `http://your-host:8000/api/best-move`

### Railway

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the `railway.json` configuration
3. Set environment variables in Railway dashboard if needed
4. Deploy with a single click

### Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Render will automatically detect the `render.yaml` configuration
4. Configure environment variables in Render dashboard
5. Deploy

### Heroku

1. Install Heroku CLI: `brew install heroku` (macOS) or `npm install -g heroku`
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Deploy: `git push heroku main`
5. View logs: `heroku logs --tail`

### Docker Hub

```bash
# Build image
docker build -t yourusername/stockfish-api:latest .

# Push to Docker Hub
docker push yourusername/stockfish-api:latest

# Run from Docker Hub
docker run -p 8000:8000 yourusername/stockfish-api:latest
```

## Performance Optimization

### Search Depth vs Speed Trade-off

| Depth | Typical Time | Use Case |
|-------|-------------|----------|
| 10 | < 100ms | Real-time web applications |
| 15 | 200-500ms | Interactive analysis |
| 20 | 1-3 seconds | Standard analysis |
| 25 | 5-15 seconds | Deep analysis |
| 30+ | 30+ seconds | Offline analysis |

### Memory Configuration

- **512 MB** (default): Suitable for most use cases
- **1024 MB**: Better for deeper analysis
- **2048 MB+**: For intensive analysis on high-end servers

### Thread Configuration

- **1-2 threads**: Low-resource environments
- **4 threads** (default): Balanced performance
- **8+ threads**: High-performance servers

## Troubleshooting

### Stockfish Binary Not Found

**Error**: `RuntimeError: Stockfish binary not found at /usr/games/stockfish`

**Solution**: 
1. Verify Stockfish installation: `which stockfish`
2. Update `STOCKFISH_PATH` in `.env` to the correct path
3. Or install Stockfish: `sudo apt-get install stockfish`

### Engine Not Ready

**Error**: `HTTPException: Stockfish engine is not ready`

**Solution**:
1. Check if Stockfish is installed and accessible
2. Verify sufficient system resources (RAM, CPU)
3. Check API logs for initialization errors
4. Restart the API service

### Invalid FEN String

**Error**: `HTTPException: Invalid FEN`

**Solution**:
1. Validate FEN using `/api/validate-fen` endpoint
2. Use `/api/starting-position` to get a valid FEN
3. Refer to FEN notation specification

## API Rate Limiting

Currently, there is no built-in rate limiting. For production deployments, consider:

1. Using a reverse proxy (Nginx, Caddy) with rate limiting
2. Implementing application-level rate limiting with middleware
3. Using a CDN with rate limiting capabilities (Cloudflare, AWS CloudFront)

## Security Considerations

1. **Input Validation**: All FEN strings are validated before processing
2. **CORS**: Configured to accept requests from any origin (adjust for production)
3. **Error Handling**: Detailed error messages for debugging (consider sanitizing for production)
4. **Resource Limits**: Set appropriate depth limits to prevent resource exhaustion

For production deployments, consider:
- Restricting CORS origins
- Implementing authentication/authorization
- Adding request logging and monitoring
- Setting up rate limiting
- Using HTTPS/TLS encryption

## Architecture

The API is built with:

- **FastAPI**: Modern Python web framework with automatic OpenAPI documentation
- **Uvicorn**: ASGI server for high-performance async request handling
- **python-chess**: Chess library for FEN validation and move generation
- **Stockfish 18**: State-of-the-art open-source chess engine

### Request Flow

```
HTTP Request → FastAPI Router → Pydantic Validation → 
Stockfish Engine → Analysis → Response Serialization → HTTP Response
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Code Formatting

```bash
# Format code with Black
black main.py

# Check code style with Flake8
flake8 main.py
```

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues, questions, or suggestions:

1. Check existing GitHub issues
2. Create a new issue with detailed description
3. Include error logs and reproduction steps

## Acknowledgments

- **Stockfish**: The powerful open-source chess engine
- **FastAPI**: Modern web framework for building APIs
- **python-chess**: Python chess library

## References

- [Stockfish Official Website](https://stockfishchess.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [UCI Protocol Specification](http://wbec-ridderkerk.nl/html/UCIProtocol.html)
- [FEN Notation Guide](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation)
