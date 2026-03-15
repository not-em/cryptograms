"""FastAPI application for the cryptogram solver."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .core.exceptions import UnsolvableError
from .core.models import Puzzle
from .core.solver import Solver
from .core.words import WordBank
from .service import encrypt_cryptogram

_STATIC = Path(__file__).parent.parent / "static"

# ---------------------------------------------------------------------------
# Shared state – corpus is loaded once at startup
# ---------------------------------------------------------------------------

_word_bank: WordBank | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm the WordBank so the first request isn't slow."""
    global _word_bank
    _word_bank = WordBank(min_length=2)
    # Touch each lazy property to trigger loading now
    _ = _word_bank.words
    _ = _word_bank.bigram_frequencies
    _ = _word_bank.trigram_frequencies
    yield


app = FastAPI(title="Cryptogram Solver", lifespan=lifespan)

if _STATIC.exists():
    app.mount("/static", StaticFiles(directory=_STATIC), name="static")


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class SolveRequest(BaseModel):
    ciphertext: str
    clue: str | None = None
    locked_pairs: dict[str, str] = {}


class SolveResponse(BaseModel):
    plaintext: str
    confidence: float
    mapping: dict[str, str]


class EncryptRequest(BaseModel):
    plaintext: str
    seed: int | None = None


class EncryptResponse(BaseModel):
    ciphertext: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
def index():
    return FileResponse(_STATIC / "index.html")


@app.post("/solve", response_model=SolveResponse)
def solve(req: SolveRequest):
    """Solve a substitution cryptogram."""
    try:
        puzzle = Puzzle(
            ciphertext=req.ciphertext,
            clue=req.clue,
            locked_pairs=req.locked_pairs,
        )
        solution = Solver(word_bank=_word_bank).solve(puzzle)
        return SolveResponse(
            plaintext=solution.plaintext,
            confidence=round(solution.confidence, 4),
            mapping=solution.mapping.mapping,
        )
    except UnsolvableError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/encrypt", response_model=EncryptResponse)
def encrypt(req: EncryptRequest):
    """Encrypt plaintext with a random substitution cipher."""
    return EncryptResponse(ciphertext=encrypt_cryptogram(req.plaintext, seed=req.seed))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("cryptograms.api:app", host="127.0.0.1", port=8000, reload=True)

