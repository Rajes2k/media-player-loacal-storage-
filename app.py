import os
import mimetypes
from flask import Flask, render_template, request, jsonify, Response, send_file, abort
from werkzeug.utils import safe_join
from pathlib import Path

APP_ROOT = Path(__file__).parent.resolve()
UPLOAD_FOLDER = APP_ROOT / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

ALLOWED_EXT = {".mp4", ".mkv", ".webm", ".mov", ".ogg", ".avi", ".flv", ".ts", ".m4v", ".mp3", ".wav"}

app = Flask(__name__, static_folder="static", template_folder="templates")


def allowed(filename):
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXT


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/list")
def api_list():
    files = []
    for p in sorted(UPLOAD_FOLDER.iterdir(), key=lambda x: x.name.lower()):
        if p.is_file() and allowed(p.name):
            files.append({
                "name": p.name,
                "size": p.stat().st_size
            })
    return jsonify(files)


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return ("No file part", 400)
    f = request.files["file"]
    if f.filename == "":
        return ("No selected file", 400)
    if not allowed(f.filename):
        return ("Unsupported file type", 400)
    safe_name = f.filename.replace("/", "_").replace("\\", "_")
    dest = UPLOAD_FOLDER / safe_name
    f.save(dest)
    return ("OK", 200)


# Range-serving endpoint (so browsers can request partial bytes)
# /uploads/<filename>
@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    # safe join
    try:
        full_path = safe_join(str(UPLOAD_FOLDER), filename)
    except Exception:
        return ("Bad request", 400)
    if not full_path:
        return ("Bad request", 400)
    path_obj = Path(full_path)
    if not path_obj.exists() or not path_obj.is_file():
        return ("Not found", 404)

    file_size = path_obj.stat().st_size
    range_header = request.headers.get("Range", None)
    mime_type, _ = mimetypes.guess_type(str(path_obj))
    if mime_type is None:
        mime_type = "application/octet-stream"

    if range_header:
        # Example: "bytes=0-1023" or "bytes=1000-"
        try:
            range_value = range_header.strip().lower().split("=")[1]
            start_str, end_str = range_value.split("-")
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else file_size - 1
        except Exception:
            # fallback to full file
            start = 0
            end = file_size - 1

        if start > end or start >= file_size:
            return Response(status=416)

        length = end - start + 1
        with open(path_obj, "rb") as f:
            f.seek(start)
            data = f.read(length)

        rv = Response(data, status=206, mimetype=mime_type)
        rv.headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        rv.headers["Accept-Ranges"] = "bytes"
        rv.headers["Content-Length"] = str(length)
        return rv
    else:
        # No Range header — send full file (Flask send_file uses efficient handling)
        return send_file(str(path_obj), mimetype=mime_type, conditional=True)


if __name__ == "__main__":
    # host 0.0.0.0 so other devices on LAN can use it
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
