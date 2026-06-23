# 📷 Don Macaron Gallery — Project Documentation

> **Generated:** 2026-06-10 00:29  
> **Path:** `C:\Users\Don Macaron\Documents\_coding\Don Macaron Gallery`  
> **Stack:** FastAPI + SQLite + Pillow + ffmpeg + HTMX + Jinja2 + Docker Compose  
> **Theme:** CRT Terminal / Pixel Art (with Dark Room redesign spec)

---

## Project Overview

A self-hosted photographer CMS with a pixel-art / CRT terminal aesthetic.
Built for a single power user with a public-facing gallery for clients.
Python-first backend (FastAPI), no heavyweight JS framework.
Deploys via Docker Compose with Traefik reverse proxy.

---

## Directory Tree

### Root Files

| File | Size | Description |
|------|------|-------------|
| `.env` | 1.4 KB | Environment configuration file — admin credentials, storage paths, app settings, and site configuration. Contains sensitive values (not committed to git). |
| `.env.example` | 1.4 KB | Template environment file with placeholder values. Copy to `.env` and fill in real credentials. |
| `.gitignore` | 1.0 KB | Git ignore rules — excludes virtual environments, data directories, `.env` secrets, IDE files, OS artifacts, logs, and compiled Python files from version control. |
| `.traefik-upload.yml` | 338 B | Traefik reverse proxy configuration snippet for handling large file uploads with extended timeouts (600s read/write). |
| `Dockerfile` | 855 B | Docker image build definition — Python 3.12-slim base, installs ffmpeg for video processing, pip-installs requirements, runs Alembic migrations, starts Uvicorn with 2 workers. |
| `PLAN.md` | 26.8 KB | Comprehensive project development plan — vision, tech stack rationale, architecture diagram, database schema, file structure, feature implementation notes, design system, Docker setup, and phased development timeline. |
| `README.md` | 4.5 KB | Project overview and quick-start guide — installation instructions for dev and production, current feature list, project structure summary, tech stack table, and development phase status. |
| `REDESIGN_SPEC.md` | 33.5 KB | Detailed redesign specification for "Dark Room" theme v2 — reference analysis, color palette, typography, CSS rules, theme switch mechanism, file checklist, and complete darkroom.css content. |
| `alembic.ini` | 706 B | Alembic database migration configuration — points to SQLite database at `data/db/gallery.db` and migration scripts in `migrations/`. |
| `docker-compose.dev.yml` | 777 B | Development Docker Compose override — enables hot-reload, mounts source code, exposes port 8000 directly (no nginx), disables production nginx profile. |
| `docker-compose.yml` | 2.3 KB | Production Docker Compose setup — Traefik-integrated, mounts originals from 1TB drive, configures HTTPS via Let's Encrypt, health checks, and auto-restart. |
| `ref 1.png` | 1.8 MB | Image file (1.8 MB) |
| `ref2.png` | 94.7 KB | Image file (94.7 KB) |
| `requirements.txt` | 784 B | Python package dependencies — FastAPI, Uvicorn, SQLAlchemy, Alembic, Pillow, ffmpeg-python, python-jose, passlib, Jinja2, python-multipart, aiofiles, python-slugify. |
| `sixty_nine.py` | 3.6 KB | Utility/maintenance Python script (project-specific helper). |

### Root Directories

| Directory | Description |
|-----------|-------------|
| `REFS/` | Design reference images folder — screenshots and inspiration for UI/UX design decisions. |
| `app/` | Main application package — FastAPI app, models, routers, services, templates, and static assets. |
| `data/` | Runtime data directory (gitignored) — contains SQLite database, processed media/thumbnails, pre-built ZIPs, and original file storage. |
| `docker/` | Docker-related configuration files (nginx config, etc.). |
| `migrations/` | Alembic database migration scripts — versioned schema changes for the SQLite database. |

### `REFS/` — Design reference images folder — screenshots and inspiration for UI/UX design decisions.

| Path | Type | Size | Description |
|------|------|------|-------------|
| `📄 LOGO.ico` | file | 4.2 KB | Image file (4.2 KB) |
| `📄 Portfolio2.pdf` | file | 390.7 KB | File (390.7 KB) |
| `📁 omg_refs` | dir | — | Subdirectory: omg_refs |
| `  📄 omg_refs/63d7d03674402992901291.jpg` | file | 264.5 KB | Image file (264.5 KB) |
| `  📄 omg_refs/65aa56541b607433182211.png` | file | 173.3 KB | Image file (173.3 KB) |
| `  📄 omg_refs/65b0422375fe5603758088.jpg` | file | 597.1 KB | Image file (597.1 KB) |
| `  📄 omg_refs/65e869c236185330505595.jpg` | file | 953.4 KB | Image file (953.4 KB) |
| `  📄 omg_refs/66794ee5a450e191204011.png` | file | 1.8 MB | Image file (1.8 MB) |
| `  📄 omg_refs/672896e641db5442735305.png` | file | 892.3 KB | Image file (892.3 KB) |
| `  📄 omg_refs/674eab8e030ee241566384.png` | file | 190.4 KB | Image file (190.4 KB) |
| `  📄 omg_refs/675022dd127b8107985470.png` | file | 1.2 MB | Image file (1.2 MB) |
| `  📄 omg_refs/67dccb8ac7e94320359681.png` | file | 553.2 KB | Image file (553.2 KB) |
| `  📄 omg_refs/67fbecf7067ca444289903.jpg` | file | 849.5 KB | Image file (849.5 KB) |
| `  📄 omg_refs/67fbed74e45e6137963408.jpg` | file | 803.7 KB | Image file (803.7 KB) |
| `  📄 omg_refs/680b597df404f850253584.png` | file | 910.9 KB | Image file (910.9 KB) |
| `  📄 omg_refs/688c03ba60cab390948017.jpg` | file | 989.0 KB | Image file (989.0 KB) |
| `  📄 omg_refs/688c03ba818f1283099552.jpg` | file | 707.5 KB | Image file (707.5 KB) |
| `  📄 omg_refs/688c03ba8c806681224332.jpg` | file | 735.2 KB | Image file (735.2 KB) |
| `  📄 omg_refs/68e354a36d4b8029184028.png` | file | 1.3 MB | Image file (1.3 MB) |
| `  📄 omg_refs/Futuristic-Retro-Gaming-Website-Experience.png` | file | 279.4 KB | Image file (279.4 KB) |
| `  📄 omg_refs/Untitled(1).png` | file | 166.3 KB | Image file (166.3 KB) |
| `  📄 omg_refs/Untitled.jpg` | file | 467.6 KB | Image file (467.6 KB) |
| `  📄 omg_refs/Untitled.png` | file | 94.7 KB | Image file (94.7 KB) |
| `  📄 omg_refs/andy-foulds-2003.png` | file | 69.4 KB | Image file (69.4 KB) |
| `  📄 omg_refs/depthcore-2002.png` | file | 151.7 KB | Image file (151.7 KB) |
| `  📄 omg_refs/designgraphik-2001.png` | file | 154.4 KB | Image file (154.4 KB) |
| `  📄 omg_refs/donnie-darko-2003.png` | file | 19.6 KB | Image file (19.6 KB) |
| `  📄 omg_refs/warp-records-2001.png` | file | 25.3 KB | Image file (25.3 KB) |
| `📄 ref_analysis.json` | file | 3.2 KB | File (3.2 KB) |

### `app/` — Main application package — FastAPI app, models, routers, services, templates, and static assets.

| Path | Type | Size | Description |
|------|------|------|-------------|
| `📄 __init__.py` | file | — | App package initializer (empty). |
| `📄 auth.py` | file | 2.9 KB | JWT authentication module — password hashing (bcrypt), token creation/verification, admin login dependency, and cookie-based session management. |
| `📄 config.py` | file | 1.1 KB | Pydantic Settings class — reads `.env` file for admin credentials, storage paths, app host/port, debug flag, and site title/tagline. |
| `📄 database.py` | file | 808 B | SQLAlchemy database engine and session setup — configures SQLite connection, creates engine, session factory, and Base declarative class. |
| `📄 main.py` | file | 3.7 KB | FastAPI application factory — creates the app, registers routers (admin + public), mounts static files, configures Jinja2 templates, sets up CORS, and defines health check endpoint. |
| `📁 models` | dir | — | Subdirectory: models |
| `  📄 models/__init__.py` | file | 653 B | Models package — imports and re-exports all SQLAlchemy model classes for centralized access. |
| `  📄 models/album.py` | file | 1.3 KB | Album ORM model — id, slug, title, description, parent_id (self-referential nesting), cover_media_id, is_public, share_token, sort_order, timestamps. |
| `  📄 models/album_media.py` | file | 528 B | Album-Media many-to-many association table — links media items to albums with sort ordering. |
| `  📄 models/job.py` | file | 1.1 KB | Job ORM model — UUID id, job_type (zip/conversion/folder_scan), status, target_id/type, result_path, progress tracking (0-100), error_message, timestamps. |
| `  📄 models/media.py` | file | 1.7 KB | Media ORM model — original_filename, slug, media_type, album_id, original/web/thumb paths, file sizes, dimensions, duration, conversion_status, EXIF JSON, sort_order, timestamps. |
| `  📄 models/menu.py` | file | 1.4 KB | MenuItem ORM model — label, item_type (page/album/external), page_id, album_id, ext_url, parent_id (nesting), sort_order, is_visible, timestamps. |
| `  📄 models/page.py` | file | 1012 B | Page ORM model — slug, title, content_html (rendered), content_delta (Quill JSON for re-editing), is_published, cover_url, sort_order, timestamps. |
| `  📄 models/setting.py` | file | 2.1 KB | Setting ORM model + DEFAULT_SETTINGS — key-value store for site configuration (title, tagline, social URLs, theme colors, fonts, scanline opacity, homepage album). |
| `📁 routers` | dir | — | Subdirectory: routers |
| `  📄 routers/__init__.py` | file | — | Routers package initializer. |
| `  📁 routers/admin` | dir | — | Subdirectory: admin |
| `    📄 routers/admin/__init__.py` | file | — | Admin routers package initializer. |
| `    📄 routers/admin/albums.py` | file | 16.4 KB | Albums CRUD router — list, create, edit, delete albums; toggle public/private; generate/regenerate share tokens; set cover image; manage sub-albums. |
| `    📄 routers/admin/auth.py` | file | 1.7 KB | Admin login/logout endpoints — renders login form, validates credentials, sets JWT cookie. |
| `    📄 routers/admin/cleanup.py` | file | 3.6 KB | Orphan cleanup endpoint — finds and removes media files not associated with any album, cleans unused thumbnails. |
| `    📄 routers/admin/dashboard.py` | file | 1.8 KB | Admin dashboard page — shows stats (total albums, media, pending conversions), recent uploads, and active background jobs. |
| `    📄 routers/admin/folder_import.py` | file | 3.3 KB | Folder import endpoint — scans local directory for media files, creates album, queues conversion jobs. |
| `    📄 routers/admin/jobs.py` | file | 2.0 KB | Job status polling endpoint — HTMX fragments for live conversion progress updates in admin panel. |
| `    📄 routers/admin/media.py` | file | 4.4 KB | Media library router — grid view with type filters, assign/unassign to album, delete media, bulk operations. |
| `    📄 routers/admin/menu.py` | file | 5.1 KB | Menu management router — CRUD menu items, reorder, nest, toggle visibility. |
| `    📄 routers/admin/pages.py` | file | 7.2 KB | Pages CRUD router — create, edit, delete rich-text pages with Quill.js editor support. |
| `    📄 routers/admin/reconvert.py` | file | 2.5 KB | Reconversion endpoint — re-processes existing media files (e.g., regenerate thumbnails with new settings). |
| `    📄 routers/admin/settings.py` | file | 7.6 KB | Settings management router — read/update site settings (title, social URLs, theme colors, CRT effects, fonts, gallery display options). |
| `    📄 routers/admin/upload.py` | file | 9.3 KB | File upload endpoint — accepts single/multiple files, saves originals, queues background conversion jobs (Pillow/ffmpeg), returns job IDs for progress tracking. |
| `  📁 routers/public` | dir | — | Subdirectory: public |
| `    📄 routers/public/__init__.py` | file | — | Public routers package initializer. |
| `    📄 routers/public/downloads.py` | file | 2.4 KB | Download endpoint — serves 2K web version or original file for download, supports share token authentication. |
| `    📄 routers/public/gallery.py` | file | 10.7 KB | Public gallery routes — homepage (featured album), album detail page (media grid + sub-albums), private share token access, breadcrumb navigation. |
| `    📄 routers/public/pages.py` | file | 3.1 KB | Public page reader — renders published pages (blog posts) at `/p/{slug}`. |
| `📁 services` | dir | — | Subdirectory: services |
| `  📄 services/__init__.py` | file | — | Services package initializer. |
| `  📄 services/audio_processor.py` | file | 2.2 KB | Audio file processing — extracts metadata, generates waveform thumbnail if applicable. |
| `  📄 services/color_extractor.py` | file | 2.6 KB | Dominant color extraction from images — computes average/dominant color for album card theming. |
| `  📄 services/conversion_pipeline.py` | file | 3.9 KB | Conversion orchestration — coordinates image/video/audio processing as background tasks, updates job status in database. |
| `  📄 services/folder_scanner.py` | file | 4.7 KB | Local folder scanner — discovers media files in a directory, creates album structure, copies/links files to originals storage. |
| `  📄 services/image_processor.py` | file | 6.6 KB | Pillow-based image processing — generates 2K WebP (2048px, quality 85) and thumbnail WebP (400px, quality 80), extracts EXIF data, handles GIF first-frame extraction. |
| `  📄 services/job_runner.py` | file | 816 B | ThreadPoolExecutor singleton — manages background task execution for conversion jobs. |
| `  📄 services/video_processor.py` | file | 4.0 KB | ffmpeg-based video processing — extracts thumbnail frame at t=1s, generates web-ready version if configured. |
| `  📄 services/zip_service.py` | file | 2.8 KB | ZIP archive builder — streams original files into pre-built ZIP for album download, runs as background task. |
| `📁 static` | dir | — | Subdirectory: static |
| `  📁 static/css` | dir | — | Subdirectory: css |
| `    📄 static/css/admin.css` | file | 7.6 KB | Admin panel CSS — sidebar layout, forms, tables, buttons, dashboard widgets, upload zone styling. |
| `    📄 static/css/crt.css` | file | 6.9 KB | CRT Terminal theme CSS — phosphor green text (#33ff33), scanline overlay, vignette, pixel borders, text glow effects, VT323 font. |
| `    📄 static/css/gallery.css` | file | 8.1 KB | Gallery layout CSS — album grid, media grid, lightbox, card overlays, responsive breakpoints, hover animations. |
| `  📁 static/fonts` | dir | — | Subdirectory: fonts |
| `  📁 static/js` | dir | — | Subdirectory: js |
| `    📄 static/js/gallery.js` | file | 3.1 KB | Frontend JavaScript — lightbox open/close/navigate, keyboard shortcuts (←→ Esc F), touch swipe gestures, image preloading. |
| `📁 templates` | dir | — | Subdirectory: templates |
| `  📁 templates/admin` | dir | — | Subdirectory: admin |
| `    📄 templates/admin/_active_jobs.html` | file | 866 B | HTMX partial — active background jobs list with progress bars (auto-refreshed). |
| `    📄 templates/admin/_folder_scan_result.html` | file | 1.9 KB | HTMX partial — folder scan results display. |
| `    📄 templates/admin/_job_fragment.html` | file | 1.6 KB | HTMX partial — single job status card with progress indicator. |
| `    📄 templates/admin/_upload_results.html` | file | 639 B | HTMX partial — upload queue initialization results. |
| `    📄 templates/admin/_zip_status.html` | file | 1.8 KB | HTMX partial — ZIP build status and download button. |
| `    📁 templates/admin/albums` | dir | — | Subdirectory: albums |
| `      📄 templates/admin/albums/edit.html` | file | 17.2 KB | HTML template (17.2 KB) |
| `      📄 templates/admin/albums/list.html` | file | 5.3 KB | HTML template (5.3 KB) |
| `      📄 templates/admin/albums/new.html` | file | 1.9 KB | HTML template (1.9 KB) |
| `    📄 templates/admin/base_admin.html` | file | 3.1 KB | Admin base layout — sidebar navigation, admin header, content area, flash messages. |
| `    📄 templates/admin/cleanup.html` | file | 4.0 KB | Orphan cleanup interface — shows orphaned files, confirm deletion. |
| `    📄 templates/admin/dashboard.html` | file | 3.0 KB | Admin dashboard template — stats cards, recent uploads grid, active jobs list with HTMX auto-refresh. |
| `    📄 templates/admin/folder_import.html` | file | 1.6 KB | Folder import form — path input, scan button, results display. |
| `    📄 templates/admin/login.html` | file | 1.7 KB | Admin login page — username/password form with CRT styling. |
| `    📁 templates/admin/media` | dir | — | Subdirectory: media |
| `      📄 templates/admin/media/list.html` | file | 9.3 KB | HTML template (9.3 KB) |
| `      📄 templates/admin/media/upload.html` | file | 19.9 KB | HTML template (19.9 KB) |
| `    📁 templates/admin/menu` | dir | — | Subdirectory: menu |
| `      📄 templates/admin/menu/_items_list.html` | file | 2.0 KB | HTML template (2.0 KB) |
| `      📄 templates/admin/menu/index.html` | file | 2.8 KB | HTML template (2.8 KB) |
| `    📁 templates/admin/pages` | dir | — | Subdirectory: pages |
| `      📄 templates/admin/pages/edit.html` | file | 14.8 KB | HTML template (14.8 KB) |
| `      📄 templates/admin/pages/list.html` | file | 1.8 KB | HTML template (1.8 KB) |
| `    📄 templates/admin/reconvert_result.html` | file | 1.3 KB | Reconversion results display. |
| `    📁 templates/admin/settings` | dir | — | Subdirectory: settings |
| `      📄 templates/admin/settings/index.html` | file | 15.9 KB | HTML template (15.9 KB) |
| `  📄 templates/base.html` | file | 5.2 KB | Base Jinja2 layout — HTML head (Google Fonts, meta tags), header (logo, nav, social icons), main content block, footer (copyright, social links), CRT overlay elements. |
| `  📁 templates/public` | dir | — | Subdirectory: public |
| `    📄 templates/public/404.html` | file | 716 B | Custom 404 error page in CRT theme. |
| `    📄 templates/public/_lightbox.html` | file | 4.7 KB | Fullscreen lightbox component — image viewer with prev/next navigation, download buttons (2K + original), filename display, counter. |
| `    📄 templates/public/album.html` | file | 3.0 KB | Album detail page — breadcrumb, album title/description, sub-albums section, media grid, share/download controls. |
| `    📄 templates/public/home.html` | file | 3.5 KB | Public homepage — featured album showcase, album grid, site title/tagline. |
| `    📄 templates/public/page.html` | file | 1.6 KB | Published page reader — renders rich HTML content from Quill editor. |

### `data/` — Runtime data directory (gitignored) — contains SQLite database, processed media/thumbnails, pre-built ZIPs, and original file storage.

| Path | Type | Size | Description |
|------|------|------|-------------|
| `📁 db` | dir | — | Subdirectory: db |
| `  📄 db/gallery.db` | file | 116.0 KB | File (116.0 KB) |
| `📁 media` | dir | — | Subdirectory: media |
| `  📁 media/photos` | dir | — | Subdirectory: photos |
| `    📄 media/photos/1_thumb.webp` | file | 6.1 KB | Image file (6.1 KB) |
| `    📄 media/photos/1_web.webp` | file | 77.8 KB | Image file (77.8 KB) |
| `    📄 media/photos/2_thumb.webp` | file | 8.1 KB | Image file (8.1 KB) |
| `    📄 media/photos/2_web.webp` | file | 44.3 KB | Image file (44.3 KB) |
| `📁 originals` | dir | — | Subdirectory: originals |
| `  📄 originals/ca2155c3ce0b44ed9a67c8f5145ea09e.jpg` | file | 124.2 KB | Image file (124.2 KB) |
| `  📄 originals/e9b359104b214e6d835a5e4528f6de26.jpg` | file | 90.3 KB | Image file (90.3 KB) |
| `📁 zips` | dir | — | Subdirectory: zips |

### `docker/` — Docker-related configuration files (nginx config, etc.).

| Path | Type | Size | Description |
|------|------|------|-------------|
| `📄 nginx.conf` | file | 1.9 KB | File (1.9 KB) |

### `migrations/` — Alembic database migration scripts — versioned schema changes for the SQLite database.

| Path | Type | Size | Description |
|------|------|------|-------------|
| `📄 __init__.py` | file | — | Python module (0 B) |
| `📄 env.py` | file | 1.7 KB | Python module — Make sure app package is importable |
| `📄 script.py.mako` | file | 534 B | File (534 B) |
| `📁 versions` | dir | — | Subdirectory: versions |
| `  📄 versions/.gitkeep` | file | — | File (0 B) |
| `  📄 versions/20250506_0001_add_album_media_junction.py` | file | 1.0 KB | Python module — """add album_media junction table |

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total files | 127 |
| Total directories | 29 |
| Python files (.py) | 44 |
| HTML templates (.html) | 27 |
| CSS stylesheets (.css) | 3 |
| JavaScript files (.js) | 1 |

---

## Key Architectural Notes

- **Backend:** FastAPI (async Python) with Jinja2 templating
- **Database:** SQLite via SQLAlchemy ORM + Alembic migrations
- **Image processing:** Pillow (WebP thumbnails + 2K versions)
- **Video processing:** ffmpeg (thumbnail extraction)
- **Frontend interactivity:** HTMX + Alpine.js (no React/Vue)
- **Admin auth:** JWT tokens in cookies (bcrypt password hashing)
- **Background tasks:** ThreadPoolExecutor (no Redis/Celery needed)
- **Deployment:** Docker Compose + Traefik (HTTPS via Let's Encrypt)
- **Storage strategy:** Originals on configurable external drive, processed media on local SSD
