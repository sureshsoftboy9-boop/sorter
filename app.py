import os
import json
import shutil
import threading
import time
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
from PIL import Image

app = Flask(__name__, static_folder='static')
CORS(app)

CONFIG_FILE = 'config.json'
SESSION_FILE = 'session.json'
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff', '.tif'}
THUMBNAIL_SIZE = (400, 400)
CACHE_DIR_NAME = '.sorter_cache'

# ─── Config ────────────────────────────────────────────────────────────────

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def validate_paths(source, destination):
    if not source or not destination:
        return False, "Both source and destination paths are required."
    source = os.path.normpath(os.path.abspath(source))
    destination = os.path.normpath(os.path.abspath(destination))
    if not os.path.isdir(source):
        return False, "Source path does not exist or is not a directory."
    if source == destination:
        return False, "Source and destination cannot be the same folder."
    if destination.startswith(source + os.sep):
        return False, "Destination cannot be a subfolder of source."
    return True, "OK"

# ─── Session ───────────────────────────────────────────────────────────────

def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            return json.load(f)
    return {
        "current_index": 0,
        "actions": [],
        "skipped": [],
        "stats": {"sorted": 0, "skipped": 0, "deleted": 0}
    }

def save_session(session):
    if 'stats' not in session:
        session['stats'] = {"sorted": 0, "skipped": 0, "deleted": 0}
    with open(SESSION_FILE, 'w') as f:
        json.dump(session, f, indent=2)

# ─── Photo scanning ────────────────────────────────────────────────────────

def scan_photos(source_path):
    photos = []
    source_path = os.path.normpath(os.path.abspath(source_path))
    for fname in sorted(os.listdir(source_path)):
        ext = os.path.splitext(fname)[1].lower()
        if ext in SUPPORTED_EXTENSIONS:
            photos.append(fname)
    return photos

# ─── Thumbnail ─────────────────────────────────────────────────────────────

def get_cache_dir(source_path):
    cache_dir = os.path.join(source_path, CACHE_DIR_NAME)
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def get_thumbnail_path(source_path, filename):
    cache_dir = get_cache_dir(source_path)
    name = os.path.splitext(filename)[0]
    return os.path.join(cache_dir, f"{name}_thumb.jpg")

def generate_thumbnail(source_path, filename):
    thumb_path = get_thumbnail_path(source_path, filename)
    if os.path.exists(thumb_path):
        return thumb_path
    full_path = os.path.join(source_path, filename)
    try:
        with Image.open(full_path) as img:
            img.thumbnail(THUMBNAIL_SIZE, Image.LANCZOS)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.save(thumb_path, 'JPEG', quality=85)
        return thumb_path
    except Exception as e:
        print(f"Thumbnail error for {filename}: {e}")
        return None

def generate_thumbnails_background(source_path, filenames, start_index=0):
    def worker():
        for fname in filenames[start_index:]:
            generate_thumbnail(source_path, fname)
            time.sleep(0.01)
    t = threading.Thread(target=worker, daemon=True)
    t.start()

# ─── File operations ───────────────────────────────────────────────────────

def do_move(source_path, dest_path, filename):
    src = os.path.join(source_path, filename)
    dst = os.path.join(dest_path, filename)
    if not os.path.exists(src):
        return False, "Source file not found."
    if os.path.exists(dst):
        base, ext = os.path.splitext(filename)
        dst = os.path.join(dest_path, f"{base}_{int(time.time())}{ext}")
    os.makedirs(dest_path, exist_ok=True)
    shutil.move(src, dst)
    return True, dst

def do_copy(source_path, dest_path, filename):
    src = os.path.join(source_path, filename)
    dst = os.path.join(dest_path, filename)
    if not os.path.exists(src):
        return False, "Source file not found."
    if os.path.exists(dst):
        base, ext = os.path.splitext(filename)
        dst = os.path.join(dest_path, f"{base}_{int(time.time())}{ext}")
    os.makedirs(dest_path, exist_ok=True)
    shutil.copy2(src, dst)
    return True, dst

def do_soft_delete(source_path, filename):
    trash_path = os.path.join(source_path, '_trash')
    return do_move(source_path, trash_path, filename)

def undo_action(action, source_path):
    op = action.get('operation')
    filename = action.get('filename')
    dest = action.get('dest')
    try:
        if op in ('move', 'soft_delete') and dest and os.path.exists(dest):
            shutil.move(dest, os.path.join(source_path, filename))
            return True, "Undone"
        elif op == 'copy' and dest and os.path.exists(dest):
            os.remove(dest)
            return True, "Undone"
        elif op == 'skip':
            return True, "Undone"
    except Exception as e:
        return False, str(e)
    return False, "Cannot undo."

# ─── API Routes ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/api/config', methods=['GET'])
def get_config():
    config = load_config()
    return jsonify({
        "configured": bool(config.get('source_path') and config.get('destination_path')),
        "operation": config.get('operation', 'move'),
        "has_source": bool(config.get('source_path')),
        "has_destination": bool(config.get('destination_path')),
    })

@app.route('/api/config', methods=['POST'])
def set_config():
    data = request.json
    source = data.get('source_path', '').strip()
    destination = data.get('destination_path', '').strip()
    operation = data.get('operation', 'move')

    if operation not in ('move', 'copy'):
        return jsonify({"error": "Invalid operation."}), 400

    valid, msg = validate_paths(source, destination)
    if not valid:
        return jsonify({"error": msg}), 400

    old_config = load_config()
    new_source = os.path.normpath(os.path.abspath(source))
    new_dest = os.path.normpath(os.path.abspath(destination))
    
    # Check if source path changed (only reset session if paths changed)
    source_changed = old_config.get('source_path') != new_source
    dest_changed = old_config.get('destination_path') != new_dest
    
    config = {
        "source_path": new_source,
        "destination_path": new_dest,
        "operation": operation
    }
    save_config(config)
    
    # Only reset session if paths actually changed
    if source_changed or dest_changed:
        save_session({"current_index": 0, "actions": [], "skipped": [], "stats": {"sorted": 0, "skipped": 0, "deleted": 0}})
    
    return jsonify({"success": True})

@app.route('/api/photos/scan', methods=['GET'])
def scan():
    config = load_config()
    if not config.get('source_path'):
        return jsonify({"error": "Not configured."}), 400

    source = config['source_path']
    photos = scan_photos(source)
    session = load_session()

    generate_thumbnails_background(source, photos, session.get('current_index', 0))

    return jsonify({
        "total": len(photos),
        "current_index": session.get('current_index', 0),
        "operation": config.get('operation', 'move'),
        "stats": session.get('stats', {"sorted": 0, "skipped": 0, "deleted": 0})
    })

@app.route('/api/photos/batch', methods=['GET'])
def get_batch():
    config = load_config()
    if not config.get('source_path'):
        return jsonify({"error": "Not configured."}), 400

    source = config['source_path']
    start = int(request.args.get('start', 0))
    count = int(request.args.get('count', 10))

    photos = scan_photos(source)
    batch = photos[start:start + count]
    return jsonify({"photos": batch, "start": start, "total": len(photos)})

@app.route('/api/thumbnail/<filename>')
def thumbnail(filename):
    config = load_config()
    if not config.get('source_path'):
        return jsonify({"error": "Not configured."}), 400

    source = config['source_path']
    if os.sep in filename or '/' in filename or '..' in filename:
        return jsonify({"error": "Invalid filename."}), 400

    full_path = os.path.normpath(os.path.join(source, filename))
    if not full_path.startswith(source):
        return jsonify({"error": "Access denied."}), 403

    thumb_path = generate_thumbnail(source, filename)
    if thumb_path and os.path.exists(thumb_path):
        return send_file(thumb_path, mimetype='image/jpeg')
    if os.path.exists(full_path):
        return send_file(full_path)
    return jsonify({"error": "File not found."}), 404

@app.route('/api/fullimage/<filename>')
def full_image(filename):
    config = load_config()
    if not config.get('source_path'):
        return jsonify({"error": "Not configured."}), 400

    source = config['source_path']
    if os.sep in filename or '/' in filename or '..' in filename:
        return jsonify({"error": "Invalid filename."}), 400

    full_path = os.path.normpath(os.path.join(source, filename))
    if not full_path.startswith(source):
        return jsonify({"error": "Access denied."}), 403

    if os.path.exists(full_path):
        return send_file(full_path)
    return jsonify({"error": "File not found."}), 404

@app.route('/api/action', methods=['POST'])
def do_action():
    config = load_config()
    session = load_session()

    if not config.get('source_path'):
        return jsonify({"error": "Not configured."}), 400

    source = config['source_path']
    destination = config['destination_path']
    operation = config['operation']

    data = request.json
    action_type = data.get('action')
    filename = data.get('filename')

    if not filename or os.sep in filename or '..' in filename:
        return jsonify({"error": "Invalid filename."}), 400

    full_path = os.path.normpath(os.path.join(source, filename))
    if not full_path.startswith(source):
        return jsonify({"error": "Access denied."}), 403

    action_record = {"operation": None, "filename": filename, "dest": None, "index": session['current_index']}
    stats = session.get('stats', {"sorted": 0, "skipped": 0, "deleted": 0})

    if action_type == 'sort':
        if operation == 'move':
            ok, dest = do_move(source, destination, filename)
        else:
            ok, dest = do_copy(source, destination, filename)
        if ok:
            action_record['operation'] = operation
            action_record['dest'] = dest
            stats['sorted'] = stats.get('sorted', 0) + 1
        else:
            return jsonify({"error": dest}), 500

    elif action_type == 'skip':
        action_record['operation'] = 'skip'
        stats['skipped'] = stats.get('skipped', 0) + 1

    elif action_type == 'soft_delete':
        ok, dest = do_soft_delete(source, filename)
        if ok:
            action_record['operation'] = 'soft_delete'
            action_record['dest'] = dest
            stats['deleted'] = stats.get('deleted', 0) + 1
        else:
            return jsonify({"error": dest}), 500
    else:
        return jsonify({"error": "Unknown action."}), 400

    session['actions'].append(action_record)
    session['current_index'] = session.get('current_index', 0) + 1
    session['stats'] = stats
    save_session(session)

    return jsonify({"success": True, "stats": stats})

@app.route('/api/undo', methods=['POST'])
def undo():
    config = load_config()
    session = load_session()

    if not config.get('source_path'):
        return jsonify({"error": "Not configured."}), 400
    if not session.get('actions'):
        return jsonify({"error": "Nothing to undo."}), 400

    source = config['source_path']
    last_action = session['actions'].pop()
    ok, msg = undo_action(last_action, source)

    if ok:
        session['current_index'] = max(0, session.get('current_index', 1) - 1)
        stats = session.get('stats', {"sorted": 0, "skipped": 0, "deleted": 0})
        op = last_action.get('operation')
        if op in ('move', 'copy'):
            stats['sorted'] = max(0, stats.get('sorted', 0) - 1)
        elif op == 'skip':
            stats['skipped'] = max(0, stats.get('skipped', 0) - 1)
        elif op == 'soft_delete':
            stats['deleted'] = max(0, stats.get('deleted', 0) - 1)
        session['stats'] = stats
        save_session(session)
        return jsonify({"success": True, "filename": last_action['filename'], "stats": stats})
    else:
        session['actions'].append(last_action)
        save_session(session)
        return jsonify({"error": msg}), 500

@app.route('/api/session', methods=['GET'])
def get_session():
    session = load_session()
    return jsonify({
        "current_index": session.get('current_index', 0),
        "actions_count": len(session.get('actions', [])),
        "can_undo": len(session.get('actions', [])) > 0,
        "stats": session.get('stats', {"sorted": 0, "skipped": 0, "deleted": 0})
    })

@app.route('/api/session/reset', methods=['POST'])
def reset_session():
    save_session({"current_index": 0, "actions": [], "skipped": [], "stats": {"sorted": 0, "skipped": 0, "deleted": 0}})
    return jsonify({"success": True})

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    print("🚀 Photo Sorter running at http://localhost:5000")
    app.run(debug=True, port=5000, threaded=True)