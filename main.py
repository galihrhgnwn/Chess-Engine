"""
Stockfish 18 REST API
A FastAPI-based REST API for interacting with the Stockfish chess engine.
"""

import os
import subprocess
import json
from typing import Optional
from contextlib import asynccontextmanager

import chess
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""
    stockfish_path: str = Field(default="/usr/games/stockfish", alias="STOCKFISH_PATH")
    stockfish_threads: int = Field(default=4, alias="STOCKFISH_THREADS")
    stockfish_memory: int = Field(default=512, alias="STOCKFISH_MEMORY")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()


class StockfishEngine:
    """Wrapper for Stockfish chess engine communication."""
    
    def __init__(self, path: str, threads: int = 4, memory: int = 512):
        self.path = path
        self.threads = threads
        self.memory = memory
        self.process = None
        self.is_ready = False
    
    def start(self):
        """Start the Stockfish engine process."""
        try:
            self.process = subprocess.Popen(
                [self.path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Configure engine
            self.send_command("uci")
            self.send_command(f"setoption name Threads value {self.threads}")
            self.send_command(f"setoption name Hash value {self.memory}")
            self.send_command("isready")
            
            # Read until "readyok"
            while True:
                line = self.process.stdout.readline()
                if "readyok" in line:
                    self.is_ready = True
                    break
            
            print(f"✓ Stockfish engine started successfully")
        except FileNotFoundError:
            raise RuntimeError(f"Stockfish binary not found at {self.path}")
        except Exception as e:
            raise RuntimeError(f"Failed to start Stockfish: {str(e)}")
    
    def stop(self):
        """Stop the Stockfish engine process."""
        if self.process:
            self.send_command("quit")
            self.process.wait(timeout=5)
            self.is_ready = False
            print("✓ Stockfish engine stopped")
    
    def send_command(self, command: str) -> str:
        """Send a command to Stockfish and get response."""
        if not self.process:
            raise RuntimeError("Stockfish engine is not running")
        
        self.process.stdin.write(command + "\n")
        self.process.stdin.flush()
    
    def get_best_move(self, fen: str, depth: int = 20, movetime: Optional[int] = None) -> dict:
        """Get the best move for a given position."""
        if not self.is_ready:
            raise RuntimeError("Stockfish engine is not ready")
        
        # Validate FEN
        try:
            board = chess.Board(fen)
        except ValueError:
            raise ValueError(f"Invalid FEN: {fen}")
        
        # Send position and go command
        self.send_command(f"position fen {fen}")
        
        if movetime:
            self.send_command(f"go movetime {movetime}")
        else:
            self.send_command(f"go depth {depth}")
        
        # Parse output
        best_move = None
        info = {}
        
        while True:
            line = self.process.stdout.readline()
            
            if "bestmove" in line:
                parts = line.split()
                best_move = parts[1]
                if len(parts) > 3:
                    ponder = parts[3]
                    info["ponder"] = ponder
                break
            
            if line.startswith("info"):
                # Parse info line
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "depth":
                        info["depth"] = int(parts[i + 1])
                    elif part == "seldepth":
                        info["seldepth"] = int(parts[i + 1])
                    elif part == "score":
                        score_type = parts[i + 1]
                        score_value = int(parts[i + 2])
                        info["score"] = {
                            "type": score_type,
                            "value": score_value
                        }
                    elif part == "nodes":
                        info["nodes"] = int(parts[i + 1])
                    elif part == "nps":
                        info["nps"] = int(parts[i + 1])
                    elif part == "time":
                        info["time"] = int(parts[i + 1])
                    elif part == "pv":
                        info["pv"] = parts[i + 1:]
        
        return {
            "best_move": best_move,
            "info": info
        }
    
    def evaluate_position(self, fen: str, depth: int = 20) -> dict:
        """Evaluate a position and return the evaluation."""
        result = self.get_best_move(fen, depth)
        
        return {
            "fen": fen,
            "best_move": result["best_move"],
            "evaluation": result["info"].get("score", {}),
            "depth": result["info"].get("depth", 0),
            "nodes": result["info"].get("nodes", 0)
        }


# Global engine instance
engine: Optional[StockfishEngine] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage engine lifecycle."""
    global engine
    
    # Startup
    engine = StockfishEngine(
        path=settings.stockfish_path,
        threads=settings.stockfish_threads,
        memory=settings.stockfish_memory
    )
    engine.start()
    
    yield
    
    # Shutdown
    if engine:
        engine.stop()


# Initialize FastAPI app
app = FastAPI(
    title="Stockfish 18 REST API",
    description="A REST API for interacting with the Stockfish chess engine",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class BestMoveRequest(BaseModel):
    """Request model for getting best move."""
    fen: str = Field(..., description="Chess position in FEN notation")
    depth: int = Field(default=20, ge=1, le=32, description="Search depth (1-32)")
    movetime: Optional[int] = Field(default=None, ge=100, description="Time limit in milliseconds")


class EvaluationRequest(BaseModel):
    """Request model for position evaluation."""
    fen: str = Field(..., description="Chess position in FEN notation")
    depth: int = Field(default=20, ge=1, le=32, description="Search depth (1-32)")


class BestMoveResponse(BaseModel):
    """Response model for best move."""
    fen: str
    best_move: str
    info: dict


class EvaluationResponse(BaseModel):
    """Response model for evaluation."""
    fen: str
    best_move: str
    evaluation: dict
    depth: int
    nodes: int


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    engine_ready: bool
    version: str


# API Endpoints

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Check API and engine health status."""
    return {
        "status": "healthy",
        "engine_ready": engine.is_ready if engine else False,
        "version": "1.0.0"
    }


@app.post("/api/best-move", response_model=BestMoveResponse, tags=["Analysis"])
async def get_best_move(request: BestMoveRequest):
    """
    Get the best move for a given chess position.
    
    **Parameters:**
    - `fen`: Chess position in FEN notation
    - `depth`: Search depth (default: 20, range: 1-32)
    - `movetime`: Optional time limit in milliseconds
    
    **Returns:**
    - `best_move`: The best move in UCI notation
    - `info`: Additional analysis information (depth, score, nodes, etc.)
    """
    if not engine or not engine.is_ready:
        raise HTTPException(status_code=503, detail="Stockfish engine is not ready")
    
    try:
        result = engine.get_best_move(
            fen=request.fen,
            depth=request.depth,
            movetime=request.movetime
        )
        return {
            "fen": request.fen,
            "best_move": result["best_move"],
            "info": result["info"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/evaluate", response_model=EvaluationResponse, tags=["Analysis"])
async def evaluate_position(request: EvaluationRequest):
    """
    Evaluate a chess position and return the best move with evaluation.
    
    **Parameters:**
    - `fen`: Chess position in FEN notation
    - `depth`: Search depth (default: 20, range: 1-32)
    
    **Returns:**
    - `best_move`: The best move in UCI notation
    - `evaluation`: Position evaluation (score and type)
    - `depth`: Actual search depth achieved
    - `nodes`: Number of nodes evaluated
    """
    if not engine or not engine.is_ready:
        raise HTTPException(status_code=503, detail="Stockfish engine is not ready")
    
    try:
        result = engine.evaluate_position(
            fen=request.fen,
            depth=request.depth
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@app.get("/api/validate-fen", tags=["Utilities"])
async def validate_fen(fen: str = Query(..., description="FEN string to validate")):
    """
    Validate a FEN string.
    
    **Parameters:**
    - `fen`: Chess position in FEN notation
    
    **Returns:**
    - `valid`: Whether the FEN is valid
    - `message`: Validation message
    """
    try:
        board = chess.Board(fen)
        return {
            "valid": True,
            "message": "Valid FEN",
            "fen": fen
        }
    except ValueError as e:
        return {
            "valid": False,
            "message": str(e),
            "fen": fen
        }


@app.get("/api/starting-position", tags=["Utilities"])
async def get_starting_position():
    """Get the starting chess position in FEN notation."""
    return {
        "fen": chess.STARTING_FEN,
        "description": "Standard chess starting position"
    }


@app.get("/", tags=["System"])
async def root():
    """API root endpoint with documentation links."""
    return {
        "name": "Stockfish 18 REST API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development"
    )
