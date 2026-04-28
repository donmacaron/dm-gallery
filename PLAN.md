# 📷 Don Macaron Gallery — Full Development Plan

> **Project folder:** `C:\Users\Don Macaron\Documents\_coding\Don Macaron Gallery`
> **Date:** 2026-04-28
> **Status:** Pre-development / Planning

---

## 1. VISION

A self-hosted photographer CMS with a **pixel-art / old CRT terminal** aesthetic. Fast, minimal dependencies, deployable via Docker Compose. Built for one power user (you) with a public-facing gallery for clients. Python-first backend, no heavyweight JavaScript framework.

---

## 2. RECOMMENDED TECH STACK

### Why this stack?

> You know Python → we stay in Python-land as much as possible.
> Self-hosted → everything runs in Docker.
> Photographer → performance on images is non-negotiable.

| Layer | Choice | Why |
|---|---|---|
| **Backend** | **FastAPI** (Python) | Async-native, handles concurrent uploads, built-in background tasks, auto-docs. Way faster than Flask for file I/O. |
| **Database** | **SQLite** → upgradeable to PostgreSQL | Zero extra service, perfect for single-user CMS. SQLAlchemy ORM makes migration trivial later. |
| **ORM / Migrations** | **SQLAlchemy** + **Alembic** | Industry standard, great for schema evolution. |
| **Image Processing** | **Pillow** (PIL) | Pure Python, handles resize → WebP, EXIF, thumbnails. |
| **Video Thumbnails** | **ffmpeg** (via subprocess) | The standard. Called via Python subprocess or `ffmpeg-python`. |
| **Rich Text Editor** | **Quill.js** | MS-Word-like, lightweight, outputs clean HTML + Delta JSON. Embeds in any template. |
| **Frontend templating** | **Jinja2** | Built into FastAPI, stays in Python world. |
| **Frontend interactivity** | **HTMX** + **Alpine.js** | HTMX = dynamic updates without writing JS. Alpine = tiny client-side state. Together they replace 90% of React/Vue use cases. |
| **CSS** | **Custom vanilla CSS** (pixel art theme) | No Tailwind. Hand-crafted CRT/terminal vibe. Full control. |
| **Static file serving** | **Nginx** | Serves media files directly, bypasses Python = 10× faster. |
| **Background tasks** | **FastAPI BackgroundTasks** + **Python ThreadPoolExecutor** | Built-in, no Redis/Celery needed for single-user. |
| **Deployment** | **Docker Compose** | `docker compose up` and done. Volumes for separate drives. |

### Dependency Summary

```
# requirements.txt
fastapi
uvicorn[standard]
sqlalchemy
alembic
python-multipart          # file uploads
pillow                    # image processing
aiofiles                  # async file ops
python-jose[cryptography] # JWT auth for admin
passlib[bcrypt]           # password hashing
jinja2
itsdangerous              # CSRF / share tokens
ffmpeg-python             # video thumbnails
python-slugify            # URL slug generation
```

---

## 3. ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│                     DOCKER COMPOSE                      │
│                                                         │
│  ┌──────────────┐    ┌──────────────────────────────┐  │
│  │    NGINX     │    │         FASTAPI APP           │  │
│  │              │◄───┤                               │  │
│  │ /media/*     │    │  /admin/*   → Admin Panel     │  │
│  │ /static/*    │    │  /api/*     → JSON API        │  │
│  │              │    │  /          → Public Gallery  │  │
│  └──────────────┘    └──────────────────────────────┘  │
│                                │                        │
│              ┌─────────────────┼──────────────┐        │
│              │                 │              │         │
│         ┌────▼────┐    ┌───────▼──────┐  ┌───▼─────┐  │
│         │ SQLite  │    │  /media/web  │  │/originals│  │
│         │   DB    │    │  thumbnails  │  │(volume → │  │
│         └─────────┘    │  2K versions │  │any drive)│  │
│                         └─────────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Storage Strategy

| Storage Volume | Contains | Docker Volume |
|---|---|---|
| `./data/media/` | Thumbnails, 2K web versions, audio | `./data/media:/app/media` |
| `ORIGINALS_PATH` | Original uploaded files | Configurable in `.env` → any local drive |
| `./data/db/` | SQLite database file | `./data/db:/app/db` |
| `./data/zips/` | Pre-built ZIP archives | `./data/zips:/app/zips` |

---

## 4. DATABASE SCHEMA

### Tables Overview

```
albums ──┐
  (self-referential parent_id for nesting)
  │
  └──► media ──► jobs (conversion status)
  
pages
menu_items (self-referential parent_id)
settings (key-value store for theme/config)
jobs (background task status: zip, conversion, folder scan)
```

### Full Schema

#### `albums`
```sql
id            INTEGER PRIMARY KEY
slug          TEXT UNIQUE NOT NULL
title         TEXT NOT NULL
description   TEXT
parent_id     INTEGER REFERENCES albums(id)  -- nested albums
cover_media_id INTEGER REFERENCES media(id)
is_public     BOOLEAN DEFAULT FALSE
share_token   TEXT UNIQUE                    -- for private client sharing
sort_order    INTEGER DEFAULT 0
created_at    DATETIME
updated_at    DATETIME
```

#### `media`
```sql
id                  INTEGER PRIMARY KEY
original_filename   TEXT NOT NULL           -- as uploaded
slug                TEXT UNIQUE NOT NULL
media_type          TEXT                    -- photo/video/gif/audio
album_id            INTEGER REFERENCES albums(id)  -- nullable = unassigned
original_path       TEXT                    -- path on originals drive
web_path            TEXT                    -- 2K WebP version
thumb_path          TEXT                    -- thumbnail WebP
file_size_original  INTEGER
file_size_web       INTEGER
width               INTEGER
height              INTEGER
duration_seconds    FLOAT                   -- for video/audio
conversion_status   TEXT DEFAULT 'pending'  -- pending/processing/done/error
conversion_error    TEXT
exif_json           TEXT                    -- raw EXIF as JSON
sort_order          INTEGER DEFAULT 0
created_at          DATETIME
updated_at          DATETIME
```

#### `pages`
```sql
id            INTEGER PRIMARY KEY
slug          TEXT UNIQUE NOT NULL
title         TEXT NOT NULL
content_html  TEXT                    -- rendered HTML from Quill
content_delta TEXT                    -- Quill Delta JSON (for re-editing)
is_published  BOOLEAN DEFAULT FALSE
cover_url     TEXT                    -- optional header image URL
sort_order    INTEGER DEFAULT 0
created_at    DATETIME
updated_at    DATETIME
```

#### `menu_items`
```sql
id          INTEGER PRIMARY KEY
label       TEXT NOT NULL
item_type   TEXT                    -- 'page' | 'album' | 'external'
page_id     INTEGER REFERENCES pages(id)
album_id    INTEGER REFERENCES albums(id)
ext_url     TEXT                    -- for external links
parent_id   INTEGER REFERENCES menu_items(id)
sort_order  INTEGER DEFAULT 0
is_visible  BOOLEAN DEFAULT TRUE
created_at  DATETIME
updated_at  DATETIME
```

#### `jobs`
```sql
id            TEXT PRIMARY KEY        -- UUID
job_type      TEXT                    -- 'zip' | 'conversion' | 'folder_scan'
status        TEXT DEFAULT 'pending'  -- pending/running/done/error
target_id     INTEGER                 -- album_id for zip jobs
target_type   TEXT                    -- 'album' | 'media'
result_path   TEXT                    -- output file path when done
progress      INTEGER DEFAULT 0       -- 0-100
total_items   INTEGER DEFAULT 0
done_items    INTEGER DEFAULT 0
error_message TEXT
created_at    DATETIME
updated_at    DATETIME
```

#### `settings`
```sql
key         TEXT PRIMARY KEY
value       TEXT
description TEXT
```

Default settings rows:
- `site_title`, `site_tagline`
- `social_telegram_url`, `social_instagram_url`
- `theme_bg_color` (#0a0a0a), `theme_fg_color` (#33ff33)
- `theme_accent_color` (#ff6600)
- `theme_scanline_opacity` (0.05)
- `theme_font` (default: `"VT323"` or `"Share Tech Mono"`)
- `homepage_album_id` (featured album on home)

---

## 5. FILE/FOLDER STRUCTURE

```
don_macaron_gallery/
│
├── app/
│   ├── main.py                     # FastAPI app factory
│   ├── config.py                   # Pydantic settings (reads .env)
│   ├── database.py                 # SQLAlchemy engine + session
│   ├── auth.py                     # JWT admin auth
│   │
│   ├── models/                     # SQLAlchemy ORM models
│   │   ├── album.py
│   │   ├── media.py
│   │   ├── page.py
│   │   ├── menu.py
│   │   ├── job.py
│   │   └── setting.py
│   │
│   ├── schemas/                    # Pydantic schemas (request/response)
│   │   ├── album.py
│   │   ├── media.py
│   │   ├── page.py
│   │   └── job.py
│   │
│   ├── routers/
│   │   ├── public/
│   │   │   ├── gallery.py          # GET /,  /{album_slug}
│   │   │   ├── pages.py            # GET /p/{page_slug}
│   │   │   └── downloads.py        # GET /download/{media_id}/{version}
│   │   └── admin/
│   │       ├── auth.py             # POST /admin/login
│   │       ├── albums.py           # CRUD albums
│   │       ├── media.py            # Upload, convert, assign
│   │       ├── pages.py            # CRUD pages (rich text)
│   │       ├── menu.py             # CRUD menu items
│   │       ├── jobs.py             # Job status polling
│   │       ├── folder_scan.py      # Import from local folder
│   │       └── settings.py         # Appearance settings
│   │
│   ├── services/
│   │   ├── image_processor.py      # Pillow: thumbnail + 2K WebP
│   │   ├── video_processor.py      # ffmpeg: thumb + web-ready
│   │   ├── zip_service.py          # Background zip builder
│   │   ├── folder_scanner.py       # Scan dir → create album
│   │   └── job_runner.py           # ThreadPoolExecutor wrapper
│   │
│   ├── templates/
│   │   ├── base.html               # CRT/pixel art base layout
│   │   ├── public/
│   │   │   ├── home.html
│   │   │   ├── album.html
│   │   │   ├── page.html
│   │   │   └── _lightbox.html      # Fullscreen component
│   │   └── admin/
│   │       ├── base_admin.html
│   │       ├── login.html
│   │       ├── dashboard.html
│   │       ├── albums/
│   │       ├── media/
│   │       ├── pages/
│   │       ├── menu/
│   │       └── settings/
│   │
│   └── static/
│       ├── css/
│       │   ├── crt.css             # CRT scanline + glow effects
│       │   ├── gallery.css         # Grid, lightbox
│       │   └── admin.css
│       ├── js/
│       │   ├── htmx.min.js
│       │   ├── alpine.min.js
│       │   ├── quill.min.js
│       │   └── gallery.js          # Lightbox logic, keyboard nav
│       └── fonts/
│           └── VT323-Regular.ttf   # Pixel font
│
├── migrations/                     # Alembic migration files
│   ├── env.py
│   └── versions/
│
├── docker/
│   ├── Dockerfile
│   └── nginx.conf
│
├── data/                           # gitignored, created on first run
│   ├── media/                      # web versions + thumbnails
│   ├── db/                         # SQLite file
│   └── zips/                       # pre-built ZIPs
│
├── docker-compose.yml
├── docker-compose.dev.yml          # dev overrides (hot reload, no nginx)
├── .env.example
├── requirements.txt
├── alembic.ini
└── README.md
```

---

## 6. KEY FEATURES — IMPLEMENTATION NOTES

### 6.1 Image Conversion Pipeline

```
Upload → Save original → Queue conversion job → Return immediately
                              ↓
                    BackgroundTask picks up job
                              ↓
                    Pillow: resize to 2048px longest side → WebP
                    Pillow: resize to 400px → WebP thumbnail
                              ↓
                    Update media.conversion_status = 'done'
                              ↓
                    Admin panel polls /api/jobs/{job_id}/status
                    → Shows progress bar per image
```

**Pillow conversion settings:**
- Format: **WebP** (30-50% smaller than JPEG, universal browser support)
- Web version: longest side = 2048px, quality = 85
- Thumbnail: longest side = 400px, quality = 80
- Preserve aspect ratio, no upscaling

### 6.2 ZIP Pre-building

```
Admin toggles "Auto-ZIP" on album → checkbox stored in albums table
                    ↓
After all uploads finish → zip_service.py triggered as BackgroundTask
                    ↓
Jobs table entry: job_type='zip', album_id=X, status='running'
                    ↓
Streams originals into ZIP file in /app/zips/{album_slug}_{hash}.zip
                    ↓
status='done', result_path set
                    ↓
Admin/client page polls /api/jobs/{job_id}/status every 3s (via HTMX)
                    ↓
When done → "⬇ Download ZIP" button appears
```

### 6.3 Albums Within Albums

- `parent_id` FK in `albums` table (self-referential)
- Public gallery renders breadcrumb path: `Portfolio / Weddings / 2025 / Anna & Peter`
- Depth is unlimited but recommend max 3-4 levels for UX
- Admin panel shows tree view of album hierarchy

### 6.4 Private Albums + Client Sharing

- `is_public = False` + `share_token = uuid4().hex`
- Public URL: `/s/{share_token}` — shows album without login
- Admin can regenerate token (invalidates old link)
- No password needed — token IS the password (send link to client)

### 6.5 Folder Import

```
Admin inputs: local folder path
                    ↓
folder_scanner.py lists all media files
                    ↓
Creates album from folder name
                    ↓
Copies/links files → originals storage
                    ↓
Queues conversion jobs for all files
                    ↓
Returns job_id for progress tracking
```

### 6.6 Global Media Library

- `/admin/media/` — shows ALL uploaded media regardless of album
- Filter tabs: **All | Photos | Videos | GIFs | Audio | Unassigned**
- Checkbox-select multiple → "Create album from selection" action
- Drag-and-drop to assign to album (HTMX + Alpine.js)
- Sort by: Date uploaded, Type, Album, Name

### 6.7 Rich Text Pages (Quill.js)

- Quill toolbar: bold, italic, headings (H1-H3), lists, links, image upload, video embed
- Images in pages: uploaded to `/media/pages/` → stored as web-optimized versions
- Output: `content_html` for display, `content_delta` for re-editing
- Autosave draft every 30s (localStorage + HTMX)

### 6.8 Fullscreen Lightbox

- Pure CSS + vanilla JS (no jQuery)
- Keyboard: ← → navigate, Esc close, F toggle fullscreen
- Swipe support (touch events) for mobile
- Two download buttons:
  - **⬇ 2K** → downloads `web_path` (2048px WebP)
  - **⬇ Original** → streams from `original_path` (full quality)
- Shows conversion status if image not yet processed

### 6.9 Menu System

- Each menu item links to: `page` | `album` | external URL
- Nested menu (1 level deep for simplicity)
- Drag-and-drop reorder (HTMX Sortable integration)
- Customizable: show/hide items, rename labels
- Social icons (Telegram, Instagram) as fixed footer items, URL set in Settings

---

## 7. PERFORMANCE STRATEGIES

| Strategy | Implementation |
|---|---|
| **Nginx serves media directly** | All `/media/*` requests served by Nginx, never hits Python |
| **WebP everywhere** | 40% smaller than JPEG, same quality perception |
| **Lazy loading** | `loading="lazy"` on all `<img>` + IntersectionObserver for custom |
| **Blur placeholder** | Store dominant color (or tiny 20px blur) in DB → show while loading |
| **Thumbnail-first** | Gallery grid loads thumbnails (400px), lightbox loads 2K on demand |
| **Preload neighbors** | In lightbox: preload next/prev image in background |
| **ZIP pre-built** | ZIP created during upload, not on download request |
| **DB indexes** | Index on `album_id`, `media_type`, `conversion_status`, `share_token` |
| **Gzip/Brotli** | Nginx gzip for HTML/CSS/JS |
| **Browser cache** | Nginx `Cache-Control: max-age=31536000` for immutable media files |

---

## 8. DESIGN SYSTEM — CRT / PIXEL ART THEME

### Color Palette (customizable via Settings)

| Token | Default | Meaning |
|---|---|---|
| `--bg` | `#0a0a0a` | Near-black background |
| `--fg` | `#33ff33` | Phosphor green text |
| `--accent` | `#ff6600` | CRT amber for highlights |
| `--dim` | `#1a1a1a` | Card/panel backgrounds |
| `--border` | `#2a2a2a` | Subtle borders |
| `--glow` | `rgba(51,255,51,0.15)` | Text shadow glow |

### Typography

- **Primary font:** `VT323` (Google Fonts) — pixel-perfect monospace
- **Body font:** `Share Tech Mono` — readable monospace
- **Fallback:** `Courier New`, monospace
- All sizes in `rem`, base 16px

### CRT Effects (CSS only, toggleable)

```css
/* Scanlines overlay */
body::after {
  content: '';
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0,0,0,0.05) 2px,
    rgba(0,0,0,0.05) 4px
  );
  pointer-events: none;
  z-index: 9999;
}

/* Phosphor glow on text */
.glow {
  text-shadow: 0 0 8px var(--glow), 0 0 20px var(--glow);
}

/* Pixel border (no border-radius — ever) */
.card {
  border: 1px solid var(--border);
  box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
}
```

### Desktop Layout (ref1.jpg inspired)

```
┌──────────────────────────────────────────────────────┐
│  [LOGO / SITE TITLE]          [@telegram] [@insta]  │
├──────────────────────────────────────────────────────┤
│  [MENU ITEM 1] [MENU ITEM 2] [MENU ITEM 3] [...]    │
├──────────────────────────────────────────────────────┤
│                                                      │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│   │  IMG 1  │ │  IMG 2  │ │  IMG 3  │ │  IMG 4  │  │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│   │  IMG 5  │ │  IMG 6  │ │  IMG 7  │ │  IMG 8  │  │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘  │
│                                                      │
├──────────────────────────────────────────────────────┤
│  © DON MACARON  |  [TELEGRAM]  [INSTAGRAM]          │
└──────────────────────────────────────────────────────┘
```

### Mobile Layout (mobile-first)

- Single column, full-width images
- Hamburger menu (pure CSS toggle, no JS)
- Touch-friendly tap targets (min 48px)
- Lightbox fullscreen works with swipe

---

## 9. DOCKER COMPOSE SETUP

### `docker-compose.yml`

```yaml
version: "3.9"

services:
  app:
    build: .
    restart: unless-stopped
    env_file: .env
    volumes:
      - ./data/media:/app/media        # thumbnails + web versions
      - ./data/db:/app/db              # SQLite database
      - ./data/zips:/app/zips          # pre-built ZIPs
      - ${ORIGINALS_PATH}:/app/originals  # ← change in .env = any drive!
    expose:
      - "8000"
    depends_on: []

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ./data/media:/var/www/media:ro     # nginx serves media directly
      - ./app/static:/var/www/static:ro    # nginx serves static assets
    depends_on:
      - app
```

### `.env.example`

```env
# Admin credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_me_please
SECRET_KEY=generate_a_long_random_string_here

# Storage paths
ORIGINALS_PATH=./data/originals   # Change to: /mnt/external_drive/photos

# App settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=false
```

### `Dockerfile`

```dockerfile
FROM python:3.12-slim

# Install ffmpeg for video processing
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini .

# Run DB migrations then start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

---

## 10. ADMIN PANEL — KEY SCREENS

### Dashboard
- Stats: total albums, total media, pending conversions
- Recent uploads
- Active background jobs (conversions, ZIPs) with live progress

### Media Library (`/admin/media/`)
- Grid view of ALL media (thumbnails)
- Filter bar: All / Photos / Videos / GIFs / Audio / Unassigned
- Conversion status badge on each thumbnail (✅ / 🔄 / ❌)
- Checkbox multi-select → "Create album", "Move to album", "Delete"
- Bulk upload zone (drag-and-drop, or click to select multiple files)
- "Import from folder" button → inputs local path → scans + queues

### Album Editor (`/admin/albums/{id}/`)
- Album metadata (title, description, slug, public/private, cover image)
- Media grid within album (reorderable via drag)
- ZIP toggle: "Pre-build ZIP for download" → shows job status
- Share link generator (for private albums)
- "Add sub-album" button

### Page Editor (`/admin/pages/{id}/`)
- Quill.js editor (full toolbar)
- Title, slug, publish toggle
- Preview button (opens public view in new tab)

### Menu Manager (`/admin/menu/`)
- Visual tree of menu items
- Drag to reorder / nest
- Each item: label, type (page/album/external), visibility toggle

### Settings (`/admin/settings/`)
- Site title, tagline
- Social URLs (Telegram, Instagram)
- Theme color pickers
- CRT effects toggle (scanlines, glow)
- Font picker

---

## 11. DEVELOPMENT PHASES

### Phase 1 — Foundation (Week 1–2)
- [ ] Project scaffold (folder structure, Docker, .env)
- [ ] FastAPI app factory, config, database setup
- [ ] SQLAlchemy models + Alembic migrations
- [ ] Basic admin auth (JWT, login page)
- [ ] Nginx config + Docker Compose working
- [ ] Health check endpoint

### Phase 2 — Media Engine (Week 2–3)
- [ ] File upload endpoint (single + multi)
- [ ] Pillow image processor (thumbnail + 2K WebP)
- [ ] ffmpeg video thumbnail extractor
- [ ] Background task runner (ThreadPoolExecutor)
- [ ] Jobs table + status polling endpoint
- [ ] Originals volume mount configurable

### Phase 3 — Admin: Media & Albums (Week 3–4)
- [ ] Media library page (grid, filters)
- [ ] Bulk upload UI with progress bars
- [ ] Album CRUD (create, edit, nest, delete)
- [ ] Assign/move media between albums
- [ ] Folder import feature
- [ ] ZIP service + toggle + status display
- [ ] Conversion status badges in admin

### Phase 4 — Admin: Content & Settings (Week 4–5)
- [ ] Quill.js rich text page editor
- [ ] Pages CRUD (blog posts)
- [ ] Menu manager with drag-to-sort
- [ ] Settings page (theme, social links)
- [ ] Private album share token system

### Phase 5 — Public Frontend (Week 5–6)
- [ ] CRT/pixel art CSS theme
- [ ] Homepage (featured album or latest)
- [ ] Album/gallery grid view
- [ ] Lightbox/fullscreen viewer
- [ ] Download buttons (2K + original)
- [ ] Page/blog reader view
- [ ] Private album access via share token

### Phase 6 — Performance & Polish (Week 6–7)
- [ ] Lazy loading + blur placeholders
- [ ] Keyboard navigation in lightbox
- [ ] Mobile swipe gestures
- [ ] SEO meta tags + Open Graph
- [ ] Error pages (404, 500) in theme
- [ ] Telegram + Instagram icons/links
- [ ] README with deploy instructions
- [ ] Final design polish (ref1.jpg comparison)

---

## 12. NICE-TO-HAVES (Post-MVP)

| Feature | Effort | Notes |
|---|---|---|
| EXIF data display in lightbox | Low | Already extracted to DB |
| Watermarking on download | Medium | Pillow overlay |
| Password-protected albums | Low | Additional field + form |
| View counter per album/image | Low | Counter field in DB |
| RSS feed for blog pages | Low | Jinja2 template |
| Custom domain + HTTPS | Low | Nginx + Certbot |
| Multiple admin accounts | Medium | Roles in users table |
| S3 / Backblaze B2 storage | Medium | Replace local volume |
| Light theme toggle | Low | CSS variables swap |

---

## 13. GETTING STARTED (Day 1 Checklist)

1. `mkdir "Don Macaron Gallery" && cd "Don Macaron Gallery"`
2. `python -m venv venv && venv\Scripts\activate`
3. `pip install fastapi uvicorn sqlalchemy alembic pillow python-multipart aiofiles`
4. Create folder structure (see Section 5)
5. Copy `.env.example` → `.env`, set your admin password
6. `alembic init migrations`
7. `docker compose up --build`
8. Visit `http://localhost/admin` → log in → start uploading

---

*Plan authored: 2026-04-28*
*Stack: FastAPI + SQLite + Pillow + Nginx + Docker Compose + HTMX + Quill.js*
*Theme: Pixel Art / CRT Terminal / Phosphor Green*
