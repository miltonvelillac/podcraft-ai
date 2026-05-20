# Web Angular

Angular frontend for PodCraft AI.

This app contains the generation page, form state, API client, script/text preview, audio player, and download flow.

The UI supports:

- text input
- PDF upload
- `Podcast` generation mode
- `Read aloud` narration mode
- voice selection
- language selection
- generated audio playback and download

## Local Development

Install dependencies from the repository root:

```bash
corepack pnpm install
```

Run the Angular dev server:

```bash
npm run web:start
```

The app proxies `/api` and `/generated` to the FastAPI host on `http://localhost:8000`.

Run a production build:

```bash
npm run web:build
```
