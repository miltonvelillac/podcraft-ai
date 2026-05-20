FROM node:22-bookworm-slim

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY apps/web-angular/package.json ./apps/web-angular/package.json

RUN corepack enable
RUN corepack pnpm install --frozen-lockfile

COPY apps/web-angular ./apps/web-angular

EXPOSE 4200

CMD ["corepack", "pnpm", "--config.verify-deps-before-run=false", "--dir", "apps/web-angular", "run", "start:docker"]
