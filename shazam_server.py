"""
Shazam recognition server.

Local:
    pip install -r shazam_requirements.txt
    python shazam_server.py

Railway / Docker:
    Uses $PORT env var. See Dockerfile.
"""
import os
import tempfile
import time
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from shazamio import Shazam

ROOT = Path(__file__).parent
app = FastAPI(title="Shazam Recognizer")

# Allow github.io frontend to call this backend.
# "*" is fine for a public read-only demo endpoint.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"ok": True}


@app.post("/api/recognize")
async def recognize(file: UploadFile = File(...)):
    raw = await file.read()
    if not raw:
        raise HTTPException(400, "empty file")

    suffix = Path(file.filename or "audio").suffix or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(raw)
        tmp_path = tmp.name

    shazam = Shazam()
    started = time.perf_counter()
    try:
        result = await shazam.recognize(tmp_path)
    except Exception as e:
        raise HTTPException(500, f"shazamio error: {e}")
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
    elapsed_ms = int((time.perf_counter() - started) * 1000)

    track = result.get("track") if isinstance(result, dict) else None
    summary = None
    if track:
        images = track.get("images") or {}
        summary = {
            "title": track.get("title"),
            "subtitle": track.get("subtitle"),
            "genre": (track.get("genres") or {}).get("primary"),
            "cover": images.get("coverarthq") or images.get("coverart"),
            "shazam_url": track.get("url"),
        }

    return JSONResponse({
        "matched": bool(track),
        "elapsed_ms": elapsed_ms,
        "summary": summary,
        "raw": result,
    })


# Serve the rest of the static site (index.html, style.css, other pages, svgs, etc.)
# Mounted last so /api/recognize takes priority.
app.mount("/", StaticFiles(directory=ROOT, html=True), name="site")


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "127.0.0.1")
    uvicorn.run(app, host=host, port=port)
