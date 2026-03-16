# Stockfish 18 REST API - Usage Guide

Complete guide for using the Stockfish 18 REST API with practical examples and best practices.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication & Headers](#authentication--headers)
3. [Endpoint Reference](#endpoint-reference)
4. [Usage Examples](#usage-examples)
5. [Common Patterns](#common-patterns)
6. [Error Handling](#error-handling)
7. [Performance Tips](#performance-tips)

## Getting Started

### Base URL

```
http://localhost:8000  # Local development
https://your-domain.com  # Production
```

### API Documentation

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI JSON**: `/openapi.json`

### Health Check

Before making requests, verify the API is running:

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "engine_ready": true,
  "version": "1.0.0"
}
```

## Authentication & Headers

Currently, the API does not require authentication. However, always include proper headers:

```bash
curl -X POST http://localhost:8000/api/best-move \
  -H "Content-Type: application/json" \
  -H "Accept: application/json"
```

For production deployments, consider adding:
- API key authentication
- JWT tokens
- OAuth 2.0

## Endpoint Reference

### 1. Health Check

**Endpoint**: `GET /health`

**Purpose**: Verify API and engine status

**Response**:
```json
{
  "status": "healthy",
  "engine_ready": true,
  "version": "1.0.0"
}
```

**Status Codes**:
- `200 OK`: API is healthy

---

### 2. Get Best Move

**Endpoint**: `POST /api/best-move`

**Purpose**: Calculate the best move for a position

**Request**:
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "depth": 20,
  "movetime": null
}
```

**Parameters**:

| Parameter | Type | Required | Default | Range | Description |
|-----------|------|----------|---------|-------|-------------|
| `fen` | string | Yes | - | - | Chess position in FEN notation |
| `depth` | integer | No | 20 | 1-32 | Search depth in half-moves |
| `movetime` | integer | No | null | 100+ | Time limit in milliseconds (overrides depth) |

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
    "pv": ["e2e4", "c7c5", "g1f3", "d7d6"]
  }
}
```

**Response Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `fen` | string | The requested position |
| `best_move` | string | Best move in UCI notation (e.g., "e2e4") |
| `info.depth` | integer | Depth searched |
| `info.seldepth` | integer | Selective depth (max depth in any variation) |
| `info.score.type` | string | "cp" (centipawns) or "mate" (checkmate) |
| `info.score.value` | integer | Score value (positive = white advantage) |
| `info.nodes` | integer | Nodes evaluated |
| `info.nps` | integer | Nodes per second |
| `info.time` | integer | Time taken in milliseconds |
| `info.pv` | array | Principal variation (best line) |

**Status Codes**:
- `200 OK`: Analysis successful
- `400 Bad Request`: Invalid FEN or parameters
- `503 Service Unavailable`: Engine not ready

---

### 3. Evaluate Position

**Endpoint**: `POST /api/evaluate`

**Purpose**: Get comprehensive position evaluation

**Request**:
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

**Status Codes**:
- `200 OK`: Evaluation successful
- `400 Bad Request`: Invalid FEN
- `503 Service Unavailable`: Engine not ready

---

### 4. Validate FEN

**Endpoint**: `GET /api/validate-fen?fen=<fen_string>`

**Purpose**: Validate a FEN string

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fen` | string | Yes | FEN string to validate |

**Response (Valid)**:
```json
{
  "valid": true,
  "message": "Valid FEN",
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
}
```

**Response (Invalid)**:
```json
{
  "valid": false,
  "message": "invalid fen: expected 8 fields",
  "fen": "invalid fen string"
}
```

**Status Codes**:
- `200 OK`: Validation complete (check `valid` field)

---

### 5. Get Starting Position

**Endpoint**: `GET /api/starting-position`

**Purpose**: Get standard chess starting position

**Response**:
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "description": "Standard chess starting position"
}
```

**Status Codes**:
- `200 OK`: Success

---

## Usage Examples

### JavaScript/TypeScript

#### Basic Analysis

```javascript
async function analyzePosition(fen) {
  const response = await fetch('http://localhost:8000/api/best-move', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      fen: fen,
      depth: 20
    })
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

// Usage
const result = await analyzePosition(
  'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
);
console.log(`Best move: ${result.best_move}`);
console.log(`Evaluation: ${result.info.score.value} cp`);
```

#### With Time Limit

```javascript
async function analyzeWithTime(fen, milliseconds) {
  const response = await fetch('http://localhost:8000/api/best-move', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      fen: fen,
      movetime: milliseconds
    })
  });

  return await response.json();
}

// Analyze for 2 seconds
const result = await analyzeWithTime(fen, 2000);
```

#### Error Handling

```javascript
async function safeAnalyze(fen) {
  try {
    // Validate FEN first
    const validation = await fetch(
      `http://localhost:8000/api/validate-fen?fen=${encodeURIComponent(fen)}`
    );
    const validationData = await validation.json();

    if (!validationData.valid) {
      console.error(`Invalid FEN: ${validationData.message}`);
      return null;
    }

    // Analyze if valid
    const response = await fetch('http://localhost:8000/api/best-move', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ fen, depth: 20 })
    });

    if (response.status === 503) {
      console.error('Engine not ready');
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Request failed:', error);
    return null;
  }
}
```

### Python

#### Basic Analysis

```python
import requests

def analyze_position(fen, depth=20):
    url = 'http://localhost:8000/api/best-move'
    payload = {
        'fen': fen,
        'depth': depth
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    return response.json()

# Usage
result = analyze_position('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
print(f"Best move: {result['best_move']}")
print(f"Evaluation: {result['info']['score']['value']} cp")
```

#### Batch Analysis

```python
import requests
from concurrent.futures import ThreadPoolExecutor

def analyze_batch(fen_list, depth=20):
    def analyze(fen):
        try:
            response = requests.post(
                'http://localhost:8000/api/best-move',
                json={'fen': fen, 'depth': depth},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {'error': str(e), 'fen': fen}
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(analyze, fen_list))
    
    return results

# Usage
fen_positions = [
    'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
    'rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1'
]

results = analyze_batch(fen_positions)
for result in results:
    if 'error' not in result:
        print(f"FEN: {result['fen'][:20]}... → {result['best_move']}")
```

#### Async Analysis

```python
import asyncio
import aiohttp

async def analyze_async(fen, depth=20):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'http://localhost:8000/api/best-move',
            json={'fen': fen, 'depth': depth}
        ) as response:
            return await response.json()

async def main():
    fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    result = await analyze_async(fen)
    print(f"Best move: {result['best_move']}")

# Run
asyncio.run(main())
```

### cURL

#### Simple Request

```bash
curl -X POST http://localhost:8000/api/best-move \
  -H "Content-Type: application/json" \
  -d '{
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "depth": 20
  }'
```

#### With Pretty Output

```bash
curl -X POST http://localhost:8000/api/best-move \
  -H "Content-Type: application/json" \
  -d '{
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "depth": 20
  }' | jq '.'
```

#### Validate FEN

```bash
curl "http://localhost:8000/api/validate-fen?fen=rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR%20w%20KQkq%20-%200%201"
```

## Common Patterns

### 1. Real-time Analysis (Web Application)

For responsive web UIs, use shorter time limits:

```javascript
async function quickAnalysis(fen) {
  return await fetch('http://localhost:8000/api/best-move', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      fen: fen,
      movetime: 500  // 500ms for quick response
    })
  }).then(r => r.json());
}
```

### 2. Deep Analysis (Offline)

For offline analysis, use higher depth:

```python
def deep_analysis(fen):
    return requests.post(
        'http://localhost:8000/api/best-move',
        json={'fen': fen, 'depth': 30}
    ).json()
```

### 3. Game Analysis

Analyze all moves in a game:

```javascript
async function analyzeGame(moves) {
  const results = [];
  let fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
  
  for (const move of moves) {
    const analysis = await analyzePosition(fen);
    results.push({
      fen: fen,
      played_move: move,
      best_move: analysis.best_move,
      evaluation: analysis.info.score.value
    });
    
    // Apply move to get new FEN (requires chess library)
    fen = applyMove(fen, move);
  }
  
  return results;
}
```

### 4. Opening Book Lookup

```python
def get_opening_moves(fen, depth=15):
    """Get recommended opening moves"""
    response = requests.post(
        'http://localhost:8000/api/best-move',
        json={'fen': fen, 'depth': depth}
    )
    data = response.json()
    
    # Extract principal variation (opening line)
    return {
        'best_move': data['best_move'],
        'line': data['info'].get('pv', [])
    }
```

## Error Handling

### Common Errors

#### 1. Invalid FEN

```json
{
  "detail": "Invalid FEN: invalid fen: expected 8 fields"
}
```

**Solution**: Validate FEN using `/api/validate-fen` endpoint

#### 2. Engine Not Ready

```json
{
  "detail": "Stockfish engine is not ready"
}
```

**Solution**: Wait for engine initialization or check `/health`

#### 3. Timeout

**Solution**: Reduce `depth` or `movetime` parameter

### Retry Strategy

```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

session = create_session_with_retries()
response = session.post('http://localhost:8000/api/best-move', json=payload)
```

## Performance Tips

### 1. Optimize Depth vs Speed

| Use Case | Depth | Time | Typical Response |
|----------|-------|------|------------------|
| Real-time UI | 10-12 | <100ms | Quick feedback |
| Interactive | 15-18 | 200-500ms | Balanced |
| Analysis | 20-24 | 1-5s | Detailed |
| Deep analysis | 28-32 | 10-60s | Comprehensive |

### 2. Batch Requests

Instead of sequential requests:

```python
# ❌ Slow: Sequential
for fen in fen_list:
    result = requests.post(url, json={'fen': fen})
```

Use parallel requests:

```python
# ✅ Fast: Parallel
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(lambda f: requests.post(url, json={'fen': f}), fen_list))
```

### 3. Cache Results

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def analyze_cached(fen, depth=20):
    response = requests.post(
        'http://localhost:8000/api/best-move',
        json={'fen': fen, 'depth': depth}
    )
    return response.json()
```

### 4. Connection Pooling

```python
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

session = requests.Session()
adapter = HTTPAdapter(poolsize=10)
session.mount('http://', adapter)
session.mount('https://', adapter)
```

## Rate Limiting Recommendations

For production, implement rate limiting:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/best-move")
@limiter.limit("10/minute")
async def get_best_move(request: BestMoveRequest):
    # Implementation
    pass
```

## Monitoring & Logging

### Log Requests

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_with_logging(fen):
    logger.info(f"Analyzing position: {fen[:30]}...")
    start = time.time()
    
    result = requests.post(
        'http://localhost:8000/api/best-move',
        json={'fen': fen, 'depth': 20}
    ).json()
    
    elapsed = time.time() - start
    logger.info(f"Analysis complete: {result['best_move']} ({elapsed:.2f}s)")
    
    return result
```

## Next Steps

- Explore the [Swagger UI](/docs) for interactive API testing
- Check the [main README](README.md) for deployment options
- Review [Stockfish documentation](https://stockfishchess.org/) for engine details
