# HTTPS через Caddy (без Docker)

Caddy устанавливается на **хост** и проксирует уже запущенные backend (`127.0.0.1:8000`) и Vite (`127.0.0.1:5173`).

## Режимы

| Режим | Команда | TLS |
|-------|---------|-----|
| **Let's Encrypt** | `.\scripts\caddy-local.ps1` | Автоматически (публичный `DOMAIN`) |
| **Локальный CA** | `.\scripts\caddy-local.ps1 -Local` | `tls internal` для `localhost.tiangolo.com` |

## 1. Установка Caddy

```powershell
winget install CaddyServer.Caddy
```

## 2. Let's Encrypt

### `.env` (корень проекта)

```dotenv
DOMAIN=your-domain.com
ACME_EMAIL=you@your-domain.com
FRONTEND_HOST=https://dashboard.your-domain.com
BACKEND_CORS_ORIGINS="https://dashboard.your-domain.com"
```

### `frontend/.env`

```dotenv
VITE_API_URL=https://api.your-domain.com
VITE_CADDY_DEV=true
VITE_CADDY_HOST=dashboard.your-domain.com
```

Эталон — `.env.caddy.example` и `frontend/.env.caddy.example`.

### DNS

- `api.your-domain.com` → A на IP этой машины  
- `dashboard.your-domain.com` → тот же IP  
- Порты **80** и **443** открыты с интернета  

### Запуск

```powershell
.\scripts\caddy-local.ps1
```

Сертификаты Let's Encrypt Caddy получает и обновляет сам. `caddy trust` не нужен.

Сертификаты на диске: `%AppData%\Caddy` (Windows) или `~/.local/share/caddy` (Linux).

---

## 3. Локальная разработка

Для `localhost.tiangolo.com` (127.0.0.1) Let's Encrypt **не работает**:

```powershell
.\scripts\caddy-local.ps1 -Local
.\scripts\caddy-trust.ps1   # один раз, пока Caddy запущен
```

---

## 4. Порядок запуска

1. PostgreSQL (локально или `docker compose up db -d` — только БД)  
2. Backend: `cd backend && fastapi dev app/main.py`  
3. Frontend: `bun run dev`  
4. Caddy: `.\scripts\caddy-local.ps1` или `-Local`  

После правки `.env` перезапустите backend, Vite и Caddy.

## 5. URL

| Сервис | Адрес |
|--------|--------|
| Frontend | `https://dashboard.$DOMAIN` |
| API | `https://api.$DOMAIN` |
| Swagger | `https://api.$DOMAIN/docs` |

## 6. OSRM

`OSRM_BASE_URL=http://localhost:5000` — отдельно на хосте, Caddy не проксирует.

## 7. Типичные ошибки

| Проблема | Решение |
|----------|---------|
| ACME failed | DNS, порты 80/443, публичный `DOMAIN` |
| localhost + LE | Используйте `-Local` |
| Порт 443 | PowerShell от администратора |
| HMR через HTTPS | `VITE_CADDY_HOST=dashboard.$DOMAIN` |
