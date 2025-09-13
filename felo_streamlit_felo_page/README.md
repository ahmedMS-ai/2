# Streamlit wrapper for uploaded page

This repo wraps the provided HTML page and assets (placed in `site/`) into a Streamlit app, preserving **layout, images, and RTL**.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

- The app auto-detects the main HTML (`site/index.html` or the largest HTML file).
- Local CSS/JS are inlined; local images are embedded as base64 to ensure a single-file render.
- Remote assets (CDNs) remain linked.

## Structure
```
.
├─ app.py
├─ .streamlit/
│  └─ config.toml
├─ site/   # original uploaded files and assets
└─ requirements.txt
```

If you need a specific HTML inside `site/` to be used, rename it to `index.html`.
