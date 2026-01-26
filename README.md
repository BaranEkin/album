# Albüm

![Release](https://img.shields.io/github/v/release/BaranEkin/album)
![Python](https://img.shields.io/badge/Python-3.11+-green.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-GUI-orange.svg)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey.svg)
![AWS](https://img.shields.io/badge/AWS-S3%20%2B%20CloudFront-yellow.svg)

Desktop application for managing family digital media (photos, videos, audio) with AWS S3/CloudFront integration and YOLOv8 face detection.

---
<img width="1520" height="1065" alt="resim" src="https://github.com/user-attachments/assets/75a55876-4e6d-42d2-82d8-feffcf693475" />


## Tech Stack

- **GUI**: PyQt5
- **Database**: SQLite + SQLAlchemy ORM
- **Cloud**: AWS S3 (storage), CloudFront (CDN with signed URLs)
- **Face Detection**: DeepFace with YOLOv8 backend
- **Image Processing**: Pillow, OpenCV
- **Python**: 3.11+

## Features

### Viewing
- Dynamic resizing image viewer area that supports zoom, pan and face tag overlays
- Media metadata displays
- Slideshow with forward/backward/random modes (5s interval)
- Three themes: Light, Dark, Classic

### Media Management
- Hybrid local/cloud storage with automatic caching
- Offline mode using local cache when cloud unavailable
- Extensive media metadata: topic, title, location, date, people face tags, notes, tags, albums, privacy level
- Automatic thumbnail generation for images and video frames
- Date precision tracking
- Supported formats: Images (.jpg, .jpeg, .png), Videos (.mp4, .avi, .mov, .mpg, .wmv, .3gp, .asf), Audio (.mp3, .wav)

### Face Detection & Tagging
- Automatic face detection via YOLOv8 when adding images
- Detection data stored as comma-separated `x-y-w-h` bounding boxes
- Left-click face box to assign/edit name
- Right-click + drag to manually draw new face region
- People overlay with hover highlighting and toggle visibility

### Organization
- Hierarchical albums with parent-child relationships (stored as concatenated 3-char tags, e.g., "a01a05")
- Custom lists (JSON-persisted, supports reordering)
- Comma-separated tags
- Privacy levels filter media visibility

### Filtering
- **Quick search**: Searches across topic, title, location, people, tags, extension, date_text
- **Detailed filters**: Per-field search with operators
  - Comma (`,`): OR - `Ali, Veli` matches either
  - Plus (`+`): AND - `Ali + Veli` matches both
  - Brackets (`[]`): Grouping - `[Ali + Veli], Ayşe`
- Turkish text normalization (ı/İ/I/i treated as equivalent)
- Filter by: date range, albums, file type, people count range, creation date range, specific days/months/years/weekdays
- Sort by: date, title, location, type, people, extension

### Discovery Features
- **Latest**: Media created within configurable days (default 7)
- **Today in History**: Same day/month from previous years
- **Forgotten**: Random 100 from 5000 least-recently-viewed media (tracked via display history)

### Multi-User
- User identification via AWS IAM
- Write permission check
- Tracks created_by/modified_by per media

## Project Structure

```
album/
├── app.py                      # Entry point
├── config/
│   └── config.py               # JSON config management
├── data/
│   ├── data_manager.py         # DB operations, SQLAlchemy queries, filtering
│   ├── display_history_manager.py  # View history (JSON)
│   ├── helpers.py              # Date conversion, Turkish text utils
│   ├── media_filter.py         # Filter criteria dataclass
│   ├── media_list_manager.py   # Custom lists (JSON)
│   └── orm.py                  # SQLAlchemy models: Media, Album
├── gui/
│   ├── main/
│   │   ├── MainWindow.py       # Main window, ~1500 lines
│   │   ├── ListModelThumbnail.py   # QAbstractListModel for thumbnails
│   │   ├── LabelImageViewer.py     # QLabel with zoom/pan
│   │   ├── FaceOverlayWidget.py    # Transparent overlay for face boxes
│   │   ├── FrameBottom.py          # Info bar + controls
│   │   └── Dialog*.py              # People, Notes, Settings, Process dialogs
│   ├── add/
│   │   ├── DialogAddMedia.py       # Upload workflow with face detection
│   │   └── DialogEditMedia.py      # Extends DialogAddMedia
│   ├── filter/
│   │   └── DialogFilter.py         # Quick/detailed filter modes
│   ├── lists/
│   │   └── DialogLists.py          # List CRUD
│   ├── constants.py            # UI strings (Turkish)
│   └── ThemeManager.py         # QPalette + stylesheet generation
├── ops/
│   ├── cloud_ops.py            # S3 upload/download, CloudFront signed URLs
│   └── file_ops.py             # Local file ops, thumbnail creation
├── face_detection.py           # YOLOv8 wrapper via deepface
├── media_loader.py             # Retrieves media from local or cloud
├── logger.py                   # File-based logging
└── res/
    ├── config.json             # Runtime config
    ├── database/               # album.db, display_history.json, media_lists.json
    ├── icons/                  # 40+ PNG icons
    ├── keys/                   # CloudFront private key
    ├── media/                  # Local media cache
    └── thumbnails/             # 160x160 thumbnails
```

## Database Schema

### Media

| Column | Type | Description |
|--------|------|-------------|
| media_uuid | TEXT PK | UUID-4 |
| created_at | REAL | Unix timestamp |
| created_by | TEXT | IAM username |
| modified_at | REAL | Unix timestamp |
| modified_by | TEXT | IAM username |
| status | INTEGER | 0=deleted, 1=active, 2=modified |
| topic | TEXT | Category |
| title | TEXT | Description |
| location | TEXT | Required |
| date | REAL | Julian day |
| date_text | TEXT | DD.MM.YYYY |
| date_est | INTEGER | Precision: 7=day, 3=month, 1=year |
| rank | REAL | Order within date |
| type | INTEGER | 1=image, 2=video, 3=audio |
| extension | TEXT | File extension |
| private | INTEGER | Privacy level |
| people | TEXT | Comma-separated names |
| people_count | INTEGER | Count |
| people_detect | TEXT | Bounding boxes: x-y-w-h,x-y-w-h |
| notes | TEXT | Notes |
| tags | TEXT | Comma-separated |
| albums | TEXT | Concatenated tags: a01a05 |

### Album

| Column | Type | Description |
|--------|------|-------------|
| album_id | INTEGER PK | ID |
| tag | TEXT | 3-char identifier (a01) |
| name | TEXT | Display name |
| path | TEXT | Hierarchical path |

## S3 Bucket Structure

```
bucket/
├── media/           # {uuid}{extension}
├── thumbnails/      # {uuid}.jpg
└── album_cloud.db   # Synchronized database
```

## Dependencies

```
boto3, botocore, cryptography    # AWS
deepface, ultralytics, tf-keras  # Face detection
numpy, opencv_python, Pillow     # Image processing
PyQt5, PyQt5_sip                 # GUI
SQLAlchemy                       # ORM
pandas, tqdm                     # Utilities
```
