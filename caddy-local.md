# HTTPS через Caddy

Два способа запуска:

| Способ | Когда |
|--------|--------|
| **Docker Compose** (`service: caddy`) | Весь стек в контейнерах |
| **На хосте** (`scripts/caddy-local.ps1`) | Backend/Vite на машине, без Caddy в Docker |

Конфиг выбирается по **`ENVIRONMENT`** в `.env`:

| `ENVIRONMENT` | Docker Compose | На хосте (`caddy-local.ps1`) |
|---------------|----------------|------------------------------|
| `local` | `Caddyfile.docker.local` | `Caddyfile.local` (`-Local`) |
| `staging`, `production` | `Caddyfile.docker.prod` | `Caddyfile` (Let's Encrypt) |

---

## Docker Compose

### `.env`

```dotenv
ENVIRONMENT=local
DOMAIN=localhost.tiangolo.com
FRONTEND_HOST=https://dashboard.localhost.tiangolo.com
BACKEND_CORS_ORIGINS="https://dashboard.localhost.tiangolo.com"
```

Для продакшена в Compose:

```dotenv
ENVIRONMENT=production
DOMAIN=myproject.ru
ACME_EMAIL=you@mail.ru
FRONTEND_HOST=https://dashboard.myproject.ru
BACKEND_CORS_ORIGINS="https://dashboard.myproject.ru"
```

### Запуск

```bash
docker compose up -d
# или с пересборкой:
docker compose up -d --build
```

Caddy стартует после `backend` (healthy) и `frontend`. Порты **80** и **443** на хосте.

### URL (local)

| Сервис | Адрес |
|--------|--------|
| Frontend | https://dashboard.localhost.tiangolo.com |
| API | https://api.localhost.tiangolo.com |

Для локального TLS в браузере может понадобиться принять предупреждение (сертификат `tls internal` в volume `caddy-data`).

### Файлы

- `Caddyfile.docker.local` — `backend:8000`, `frontend:80`, `tls internal`
- `Caddyfile.docker.prod` — Let's Encrypt, `api.{$DOMAIN}`, `dashboard.{$DOMAIN}`
- `scripts/caddy-docker-entrypoint.sh` — выбор конфига по `ENVIRONMENT`

---

## Caddy на хосте (без Docker для Caddy)

### Установка

```powershell
winget install CaddyServer.Caddy
```

### Локально

```powershell
.\scripts\caddy-local.ps1 -Local
.\scripts\caddy-trust.ps1
```

Конфиг: `Caddyfile.local` → `127.0.0.1:8000`, `127.0.0.1:5173` (Vite dev).

### Продакшен на хосте

```dotenv
ENVIRONMENT=production
DOMAIN=myproject.ru
ACME_EMAIL=you@mail.ru
```

```powershell
.\scripts\caddy-local.ps1
```

Конфиг: `Caddyfile` (Let's Encrypt).

---

## OSRM

`OSRM_BASE_URL=http://localhost:5000` — отдельно на хосте, Caddy не проксирует.

## Типичные ошибки

| Проблема | Решение |
|----------|---------|
| ACME failed | `ENVIRONMENT=production`, DNS, порты 80/443 |
| localhost + production | Поставьте `ENVIRONMENT=local` |
| Caddy не стартует в Compose | `docker compose logs caddy`, проверьте backend health |
| Порт 443 занят | Остановите другой Caddy / IIS |
