from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from urllib.parse import unquote
from database.db import SessionLocal
from models.songs import Song
from models.events import Event
import re

app = FastAPI(title="HistorySounds")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows Tilda, localhost, etc. (safe for testing)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def normalize(text: str) -> str:
    if not text:
        return ""
    text = str(text).lower().strip()
    # Remove quotes, punctuation, extra spaces
    text = re.sub(r'[«»"\'`:,.;!?]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

# For Tilda

@app.get("/api/events")
def get_events(db: Session = Depends(get_db)):
    events = db.query(Event).order_by(Event.id.asc()).all()
    return[
        {
            "id": e.id,
            "preview": e.description[:120] + ("..." if len(e.description) > 120 else ""),
            "full": e.description,
            "song_count": len(e.songs)
        } for e in events
    ]

# Event details + linked songs
@app.get("/api/event/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(404, "Event not found")
    return {
        "id": event.id,
        "description": event.description,
        "songs": [
            {"name": s.name, "composer": s.composer or "Автор неизвестен"}
            for s in event.songs
        ]
    }

# Song details
@app.get("/api/song/{song_slug}")
def song_api(song_slug: str, db: Session = Depends(get_db)):
    song_q = normalize(unquote(song_slug))
    song = next((s for s in db.query(Song).all() if normalize(s.name) == song_q), None)
    if not song:
        raise HTTPException(404, "Song not found")
    return {
        "name": song.name,
        "composer": song.composer or "Автор неизвестен",
        "description": song.description,
        "events": [e.description for e in song.events]
    }

# Temporary debug route
@app.get("/api/ping")
def ping():
    return {"status": "ok", "cors_test": True}

@app.get("/event/{event_id}", response_class=HTMLResponse)
async def event_page(request: Request, event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return templates.TemplateResponse(request, "event.html", {"event": event})

@app.get("/song/{song_slug}", response_class=HTMLResponse)
async def song_page(request: Request, song_slug: str, db: Session = Depends(get_db)):
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
        raise HTTPException(status_code=404, detail="Song not found")

    return templates.TemplateResponse(request, "song.html", {"song": song})

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

    return templates.TemplateResponse(request, "song.html", {"song": song})


@app.get("/", response_class=HTMLResponse)
async def timeline(request: Request, db: Session = Depends(get_db)):
    # Order by ID
    events = db.query(Event).order_by(Event.id.asc()).all()
    return templates.TemplateResponse(request, "timeline.html", {"events": events})