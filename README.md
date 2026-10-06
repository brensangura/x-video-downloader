# X Video Downloader

## Run locally
    python -m venv venv && source venv/bin/activate
    pip install -r requirements.txt
    python app.py            # http://127.0.0.1:5000

## Deploy
    gunicorn -w 2 -b 0.0.0.0:8000 app:app
Put it behind Nginx/Caddy with HTTPS. Any small VPS (or Render/Railway/Fly) works. Behind a proxy, set the real client IP header, otherwise rate limiting sees one IP.

## Keep it working
- X changes often. Run `pip install -U yt-dlp` weekly (cron) and restart.
- Add Redis storage to flask-limiter if you run more than one worker.

## Before adding ads
- Replace YOUR-EMAIL@example.com in templates/privacy.html and keep a working takedown process.
- Paste ad code into the two "AD SLOT" blocks in templates/index.html.
