from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from urllib.parse import unquote
from database.db import SessionLocal
from models.songs import Song
from models.events import Event
import re

app = FastAPI(title="HistorySounds")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="HistorySounds")
app.mount("/static", StaticFiles(directory="static"), name="static")

def normalize(text: str) -> str:
    if not text:
        return ""
    text = str(text).lower().strip()
    # Remove quotes, punctuation, extra spaces
    text = re.sub(r'[«»"\'`:,.;!?]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text


@app.get("/song/{song_slug}", response_class=HTMLResponse)
async def song_by_name_only(request: Request, song_slug: str, db: Session = Depends(get_db)):
    from urllib.parse import unquote
    import re

    def normalize(t: str) -> str:
        if not t: return ""
        t = str(t).lower().strip()
        t = re.sub(r'[^\w\s-]', '', t)  # Strips «»""'':,.;!? etc.
        return re.sub(r'\s+', ' ', t)

    song_q = normalize(unquote(song_slug))
    song = next((s for s in db.query(Song).all() if normalize(s.name) == song_q), None)

    if not song:
        print(f"Not found by name: '{song_q}'")
        raise HTTPException(status_code=404, detail="Song not found")

    return templates.TemplateResponse("song.html", {"request": request, "song": song})


@app.get("/{composer_slug}/{song_slug}", response_class=HTMLResponse)
async def song_page(request: Request, composer_slug: str, song_slug: str, db: Session = Depends(get_db)):
    composer_q = normalize(unquote(composer_slug))
    song_q = normalize(unquote(song_slug))

    # Fetch all songs and filter in Python (flexible + debuggable)
    all_songs = db.query(Song).all()

    song = None
    for s in all_songs:
        if (normalize(s.name) == song_q and
                (not composer_q or composer_q == 'unknown' or normalize(s.composer) == composer_q)):
            song = s
            break

    if not song:
        # Debug log only - no more crashing
        print(f" Not found: composer='{composer_q}', song='{song_q}'")
        print(f"   Searched {len(all_songs)} songs")
        # Optional: show closest name matches
        close_matches = [s for s in all_songs if song_q in normalize(s.name)]
        if close_matches:
            print(f"   Close name matches: {[(s.composer, s.name) for s in close_matches[:3]]}")
        raise HTTPException(status_code=404, detail="Song not found")

    return templates.TemplateResponse(
        name="song.html",
        context={"request": request, "song": song}
    )

# For Tilda; do not use currently

@app.get("/api/song/{song_slug}")
def song_api(song_slug: str, db: Session = Depends(get_db)):
    from urllib.parse import unquote
    import re
    def normalize(t):
        return re.sub(r'\s+', ' ', re.sub(r'[«»"\'`:,.;!?]', '', str(t).lower().strip())) if t else ""

    song_q = normalize(unquote(song_slug))
    song = next((s for s in db.query(Song).all() if normalize(s.name) == song_q), None)
    if not song:
        raise HTTPException(404)
    return JSONResponse({
        "name": song.name,
        "composer": song.composer or "Unknown",
        "events": [e.description for e in song.events]
    })


@app.get("/", response_class=HTMLResponse)
async def timeline(request: Request, db: Session = Depends(get_db)):
    songs = db.query(Song).order_by(Song.composer, Song.name).all()
    return templates.TemplateResponse(
        name="timeline.html",
        context={"request": request, "songs": songs}
    )