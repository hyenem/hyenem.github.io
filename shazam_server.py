"""
Shazam recognition server.

Local:
    pip install -r shazam_requirements.txt
    python shazam_server.py

Railway / Docker:
    Uses $PORT env var. See Dockerfile.
"""
import logging
import os
import tempfile
import time
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from shazamio import Shazam

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("shazam-demo")

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
    size_kb = len(raw) / 1024
    log.info(
        "recognize: name=%r content_type=%s size_kb=%.1f suffix=%s",
        file.filename, file.content_type, size_kb, suffix,
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(raw)
        tmp_path = tmp.name

    shazam = Shazam()
    started = time.perf_counter()
    error_msg = None
    result = None
    try:
        result = await shazam.recognize(tmp_path)
    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}"
        log.exception("shazamio recognize failed")
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
    elapsed_ms = int((time.perf_counter() - started) * 1000)

    if error_msg:
        return JSONResponse(
            {"matched": False, "elapsed_ms": elapsed_ms, "summary": None,
             "error": error_msg, "raw": None},
            status_code=200,
        )

    track = result.get("track") if isinstance(result, dict) else None
    matches = result.get("matches") if isinstance(result, dict) else None
    log.info(
        "recognize result: matched=%s matches_len=%s elapsed_ms=%d",
        bool(track), len(matches) if isinstance(matches, list) else "n/a", elapsed_ms,
    )

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
