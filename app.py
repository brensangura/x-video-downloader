import re
from urllib.parse import urlparse

import yt_dlp
from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per hour"])

ALLOWED_HOSTS = {"twitter.com", "www.twitter.com", "x.com", "www.x.com", "mobile.twitter.com"}
STATUS_RE = re.compile(r"^/[^/]+/status/\d+")


def valid_post_url(url: str) -> bool:
    try:
        p = urlparse(url.strip())
    except ValueError:
        return False
    return p.scheme in ("http", "https") and p.hostname in ALLOWED_HOSTS and bool(STATUS_RE.match(p.path))


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/privacy")
def privacy():
    return render_template("privacy.html")


@app.post("/api/info")
@limiter.limit("10 per minute")
def info():
    url = (request.get_json(silent=True) or {}).get("url", "")
    if not valid_post_url(url):
        return jsonify(error="Please paste a valid post link, e.g. https://x.com/user/status/123456"), 400

    opts = {"quiet": True, "no_warnings": True, "skip_download": True, "socket_timeout": 15}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            data = ydl.extract_info(url, download=False)
    except Exception:
        return jsonify(error="Could not find a video in that post. It may be private, deleted or contain no video."), 422

    entries = data.get("entries") or [data]
    videos = []
    for e in entries:
        formats = [
            {"quality": f"{f.get('height')}p", "height": f.get("height") or 0, "url": f["url"]}
            for f in e.get("formats", [])
            if f.get("ext") == "mp4" and f.get("vcodec") != "none" and f.get("url", "").startswith("https://")
        ]
        formats.sort(key=lambda x: x["height"], reverse=True)
        if formats:
            videos.append({
                "title": (e.get("title") or "Video")[:120],
                "thumbnail": e.get("thumbnail"),
                "formats": formats,
            })
    if not videos:
        return jsonify(error="No downloadable video found in that post."), 422
    return jsonify(videos=videos)


if __name__ == "__main__":
    app.run(debug=True)
