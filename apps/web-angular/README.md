# Web Angular

Angular frontend for PodCraft AI.

This app contains the podcast generation page, form state, API client, script preview, audio player, and download flow.

## Local Development

Install dependencies from the repository root:

```bash
pnpm install
```

Run the Angular dev server:

```bash
pnpm web:start
```

The app proxies `/api` and `/generated` to the FastAPI host on `http://localhost:8000`.

Run a production build:

```bash
pnpm web:build
```
