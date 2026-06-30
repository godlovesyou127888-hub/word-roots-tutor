# Word Roots Tutor

A simple, browser-based tool for memorising 100 essential English word roots. Designed for learners who want quick, focused exposure to roots, example words, and mnemonics in a friendly reading environment.

- Project path: `C:\Users\salek\word-roots-tutor`
- Public repo: https://github.com/godlovesyou127888-hub/word-roots-tutor

## What’s inside

- `web/index.html` — a single-page browser app with large, readable layout
- `web/roots.json` — 100 roots including forms, definitions, examples, and mnemonics
- `src/` — optional command-line learning mode for Ask / Quiz / Review / List / Browse / Reset flows

## Quick start

1. Open `C:\Users\salek\word-roots-tutor\web\index.html` in a browser.
2. Or run a local server:
   ```bash
   cd C:\Users\salek\word-roots-tutor\web
   python -m http.server 8080
   ```
3. Then open `http://localhost:8080`.
4. Progress is stored in the browser.

## Deploy for free

This app is a static HTML + JSON site and can be hosted anywhere.

### GitHub Pages (recommended)

1. Push this repo to GitHub.
2. Open **Settings → Pages**.
3. Set **Source** to **Deploy from a branch**.
4. Choose branch `master` and folder `/web`.
5. Save. After a minute, your public site is available at:
   `https://godlovesyou127888-hub.github.io/word-roots-tutor/`

### Other options

- Netlify Drop: drag the `web` folder into https://app.netlify.com/drop
- Vercel: import the repo and set the publish directory to `web/`
- Any static web host

## Notes

- The JSON data uses bilingually optimised example and mnemonic fields.
- Web UI supports large-type, high-contrast display for long reading sessions.
