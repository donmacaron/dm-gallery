# 📷 Don Macaron Gallery

Self-hosted photographer CMS. Pixel-art / CRT terminal aesthetic.
Fast. Python. Docker.

---

## Quick Start (Dev — no Docker)

```bash
# 1. Create virtual env
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
copy .env.example .env
# Edit .env — set ADMIN_PASSWORD and SECRET_KEY

# 4. Run database migrations (or skip: tables auto-created on first run)
alembic upgrade head

# 5. Start dev server
uvicorn app.main:app --reload
```

Open: http://localhost:8000
Admin: http://localhost:8000/admin

---

## Production (Docker Compose)

```bash
copy .env.example .env
# Edit .env — set ADMIN_PASSWORD, SECRET_KEY, ORIGINALS_PATH

docker compose up -d
```

Open: http://localhost
Admin: http://localhost/admin

### Originals on a separate drive

Edit `.env`:
```
ORIGINALS_PATH=D:/photos/originals       # Windows
ORIGINALS_PATH=/mnt/external/photos      # Linux
```

---

## Phase 2 — What's working now

- **Upload single or multiple files** — drag-and-drop zone at `/admin/upload`
- **Background image conversion** — Pillow converts to 2K WebP + thumbnail
- **GIF thumbnail extraction** — first frame as WebP thumbnail
- **Video thumbnail extraction** — ffmpeg extracts frame at t=1s
- **Live conversion progress** — HTMX polls `/admin/api/jobs/{id}/fragment` every 2s
- **Full Albums CRUD** — create, edit, nest, toggle public/private, delete
- **Private sharing** — share token URL at `/s/{token}`, regeneratable
- **Set album cover** — pick any thumbnail from the media grid
- **Media library** — filter by type, quick-assign to album
- **Dashboard live jobs** — active conversion queue shown with auto-refresh

---

## Project Structure

```
app/
  main.py           — FastAPI app factory
  config.py         — Settings (reads .env)
  database.py       — SQLAlchemy + SQLite
  auth.py           — JWT admin auth
  models/           — DB models (Album, Media, Page, MenuItem, Job, Setting)
  routers/
    admin/
      auth.py       — Login/logout
      dashboard.py  — Dashboard with live job stats
      albums.py     — Albums CRUD + toggle/share/cover
      media.py      — Media library + assign/delete
      upload.py     — File upload + background conversion queue
      jobs.py       — HTMX polling fragments for conversion status
    public/
      gallery.py    — Public gallery pages
      downloads.py  — 2K + original file download
  services/
    image_processor.py  — Pillow: 2K WebP + thumbnail
    video_processor.py  — ffmpeg: video thumbnail
    zip_service.py      — ZIP builder (Phase 3)
    folder_scanner.py   — Folder import (Phase 3)
    job_runner.py       — ThreadPoolExecutor singleton
  templates/
    base.html             — CRT base layout
    admin/
      base_admin.html     — Admin sidebar layout
      _job_fragment.html  — HTMX: single job status card
      _upload_results.html— HTMX: upload queue init
      _active_jobs.html   — HTMX: dashboard job list
      dashboard.html
      albums/list, new, edit
      media/list, upload
    public/
      home, album, 404, _lightbox
  static/
    css/crt.css, gallery.css, admin.css
    js/gallery.js
data/
  db/       — SQLite database
  media/    — Thumbnails + 2K WebP
  originals/— Original files (configurable via ORIGINALS_PATH)
  zips/     — Pre-built ZIPs (Phase 3)
```

---

## Development Phases

- [x] **Phase 1** — Foundation: Docker, DB, auth, basic public gallery ✔
- [x] **Phase 2** — Media Engine: upload, Pillow/ffmpeg, background jobs, albums CRUD ✔
- [x] **Phase 3** — Admin: folder import, ZIP pre-builder, bulk select/create album
- [x] **Phase 4** — Content: Quill.js rich text pages, menu manager, settings UI
- [x] **Phase 5** — Public Frontend: full CRT theme, lightbox polish
- [x] **Phase 6** — Polish: lazy loading, SEO, mobile swipe, orphan cleanup

---

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI + Python 3.12 |
| Database | SQLite → SQLAlchemy + Alembic |
| Images | Pillow (WebP + thumbnails) |
| Video | ffmpeg (subprocess) |
| Frontend | Jinja2 + HTMX + Alpine.js |
| Fonts | VT323 (Google Fonts) |
| Deploy | Docker Compose + Nginx |

---

*Stack: FastAPI + SQLite + Pillow + Nginx + Docker Compose + HTMX*
*Theme: Pixel Art / CRT Terminal / Phosphor Green*
