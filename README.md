# Smart_fatilizer_recommendation


A 5-page multilingual agricultural support web app, built with **only Python (Flask)
and HTML/CSS/JS** — no paid APIs, no React, no build step.

Pages: Language & Input → Visual Confirmation → Fertilizer Recommendation →
Application Duration → Vendor Map (Leaflet + OpenStreetMap, free, no API key).

## 1. Run it locally

```bash
pip install -r requirements.txt
python app.py
```

Open **http://localhost:5000** in your browser.

## 2. Open it on your phone (same WiFi, quick demo)

1. Find your computer's local IP (Windows: `ipconfig`, Mac/Linux: `ifconfig`) — looks like `192.168.x.x`.
2. Run the app (already listens on `0.0.0.0:5000`, see `app.py`).
3. On your phone (same WiFi), open: `http://192.168.x.x:5000`
4. Tap the browser menu → **"Add to Home Screen"** — it will behave like an app icon.

## 3. Get a real public link (works anywhere, for submission/demo)

Easiest free options — pick one:

**Render.com** (recommended, free tier)
1. Push this folder to a GitHub repo.
2. On render.com → New → Web Service → connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Deploy → you get a link like `https://smart-fertilizer.onrender.com` — open it on any phone.

**PythonAnywhere** (free tier, good for college projects)
1. Upload the project files.
2. Create a new Flask web app pointing to `app.py`.
3. Reload — you get a link like `https://yourusername.pythonanywhere.com`.

**Replit**
1. Import this folder as a new Python/Flask Repl.
2. Click Run — Replit gives you a public `https://...repl.co` link instantly.

Any of these links can be opened directly on a phone browser, bookmarked, or
added to the home screen just like an app.

## Project structure
```
app.py                 # all routes + fertilizer logic + translations
templates/
  base.html             # shared layout + growth-stage progress bar
  index.html            # Page 1
  confirm.html          # Page 2
  recommend.html        # Page 3
  duration.html         # Page 4
  vendors.html          # Page 5 (map)
static/
  style.css
  icon.svg
manifest.json (served from app.py)  # lets phones "install" it
requirements.txt
Procfile                # for Render/Heroku-style hosts
```

## Customizing
- **Fertilizer data**: edit `CROP_FERTILIZER` / `CROP_STAGES` in `app.py`.
- **Vendors**: edit `VENDORS` list in `app.py` (swap in a real vendor DB + a
  geocoding service later for production use).
- **Languages**: edit the `TRANSLATIONS` dict — add more languages by copying
  the `"en"` block and translating the values.
