# 📷 PhotoSort

A fast, swipe-based photo organizer. Sort thousands of photos in seconds.

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the server
```bash
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

---

## How to Use

1. **Enter paths** — Type source and destination folder paths
2. **Choose operation** — Move (default) or Copy
3. **Click "Load Photos"** — Scans folder instantly, generates thumbnails in background
4. **Swipe to sort:**

| Gesture | Action |
|---|---|
| ← Swipe Left | Sort (move/copy to destination) |
| → Swipe Right | Skip |
| ↓ Swipe Down | Soft Delete (moves to `_trash` subfolder) |
| Ctrl+Z | Undo last action |

### Keyboard Shortcuts (Desktop)
- `←` Arrow = Sort
- `→` Arrow = Skip
- `↓` Arrow = Soft Delete
- `Ctrl+Z` = Undo

---

## Performance

- Scans 5000+ photos in under 1 second (filename index only)
- Thumbnails generated in background, cached in `.sorter_cache` folder
- Only 3 photos loaded in memory at once
- Next photos pre-loaded silently for instant swiping

## Security

- Paths validated server-side only
- Frontend never sends or sees full file paths
- Path traversal attacks blocked
- Source and destination cannot overlap

## Files Generated

| File | Purpose |
|---|---|
| `config.json` | Saved source/destination paths |
| `session.json` | Resume progress (current index, undo history) |
| `source/_trash/` | Soft-deleted photos |
| `source/.sorter_cache/` | Thumbnail cache |