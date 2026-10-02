# Emotion Radar

An emotion-based music recommendation app. Your browser's webcam feed (or an
uploaded photo) is analyzed for a face and its expression; the detected
emotion routes you to a matching playlist with a built-in music player.

## Architecture

```
Browser (getUserMedia) --frame every ~500ms--> POST /detect-emotion
                                                     |
                                          MediaPipe face detection
                                                     |
                                          DeepFace emotion classification
                                                     |
                                     JSON: {emotion, face_box, playlist_url}
                                                     |
                              canvas draws HUD box  /  redirect on request
```

- **Backend:** Django 5 + Django REST Framework
- **Face detection:** MediaPipe Face Detection (picks the single
  highest-confidence face, not every face in frame)
- **Emotion classification:** DeepFace (`actions=["emotion"]`)
- **Frontend:** vanilla JS, no build step — `getUserMedia` for the webcam,
  `fetch` to poll the backend, `<canvas>` for the HUD overlay and the
  starfield
- **Data:** SQLite, one model per mood (`neutral`, `happy`, `sad`, `fear`,
  `surprise`, `angry`), each with title/artist/audio file/cover image

## Running it locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env if you want a real SECRET_KEY (the default only works for local dev)

python manage.py migrate
python manage.py runserver
```

Visit `http://localhost:8000`. The shipped `db/db.sqlite3` already has demo
songs and cover art loaded per mood — `migrate` just brings the schema up
to date against it, it won't touch existing data.

### With Docker

```bash
cp .env.example .env
docker compose up --build
```

## Tests

```bash
pytest -v
```

Covers: signup validation, login/logout (including a regression test for
the original no-op logout), route protection (webcam/playlist require
login), the mood-URL collision bug specifically, and `/detect-emotion`'s
request handling — with the actual face/emotion models mocked out so the
suite runs fast and doesn't need a webcam or GPU.


## Possible extensions

- Swap DeepFace's dominant-emotion label for its full per-class confidence
  scores, and surface them in the HUD readout
- A `Recent Scans` history per user (mirrors the pattern used in the other
  two projects in this portfolio)
- Replace the six per-mood Django models with a single `Song` model with a
  `mood` choice field — worth doing once there's a safe way to migrate the
  existing populated database
- Rate limit `/detect-emotion` per session to bound DeepFace's CPU cost

