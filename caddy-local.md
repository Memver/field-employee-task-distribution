# Локальный HTTPS через Caddy (без Docker)

Caddy проксирует трафик на уже запущенные backend и frontend с автоматическим TLS (`tls internal`).

## 1. Установка Caddy

```powershell
winget install CaddyServer.Caddy
```

Или с [caddyserver.com/docs/install](https://caddyserver.com/docs/install#windows).

## 2. Доверие локальному CA (один раз)

**Важно:** `caddy trust` подключается к **уже запущенному** Caddy (admin API). Сначала запустите Caddy (шаг 4, терминал 4), затем в **другом** терминале:

```powershell
caddy trust --address 127.0.0.1:20190
```

Admin API слушает `127.0.0.1:20190` (см. `Caddyfile`), не стандартный `:2019` — так надёжнее на Windows.

Если видите `connectex: ... forbidden by its access permissions` на `:2019` — Caddy не был запущен, либо клиент стучится не на тот адрес. Используйте команду выше.

Установка CA в хранилище Windows может потребовать PowerShell **от администратора**. Без trust браузер покажет предупреждение о сертификате (можно принять вручную).

### Ошибка при `caddy run`: порт 443

На Windows для портов 80/443 иногда нужны права администратора. Запустите `.\scripts\caddy-local.ps1` из elevated PowerShell.

### Порт 2019 занят системой

В `Caddyfile` уже задан `admin 127.0.0.1:20190`. Для trust всегда указывайте `--address 127.0.0.1:20190`.

### Ошибка `failed to execute keytool.exe`

На Windows `caddy trust` может упасть на шаге Java (`keytool.exe`), хотя CA для **системы/браузера** уже установлен. Это не мешает работе в Chrome/Edge.

Если браузер всё ещё не доверяет сертификату:

1. Скачайте корневой сертификат (пока Caddy запущен): откройте в браузере `http://127.0.0.1:20190/pki/ca/local` и сохраните файл, **или** выполните:
   ```powershell
   Invoke-WebRequest -Uri http://127.0.0.1:20190/pki/ca/local -OutFile caddy-local-ca.crt
   ```
2. Дважды щёлкните `caddy-local-ca.crt` → «Установить сертификат» → «Локальный компьютер» → «Поместить в следующее хранилище» → **Доверенные корневые центры сертификации**.

Либо один раз нажмите «Дополнительно» → «Перейти на сайт» в предупреждении браузера.

## 3. Переменные окружения

В проекте уже настроены `.env` и `frontend/.env` под Caddy HTTPS. Эталон — `.env.caddy.example` и `frontend/.env.caddy.example`.

После любой правки env **перезапустите** backend и Vite.

## 4. Запуск сервисов

Порядок: backend и frontend → **Caddy** → при первом запуске `caddy trust`.

Терминал 1 — БД (Docker только для Postgres):

```powershell
docker compose up db -d
```

Терминал 2 — backend:

```powershell
cd backend
uv sync
fastapi dev app/main.py
```

Терминал 3 — frontend:

```powershell
bun run dev
```

Терминал 4 — Caddy:

```powershell
.\scripts\caddy-local.ps1
```

Или:

```powershell
caddy run --config Caddyfile
```

## 5. Адреса

| Сервис   | URL |
|----------|-----|
| Frontend | https://dashboard.localhost.tiangolo.com |
| API      | https://api.localhost.tiangolo.com |
| Swagger  | https://api.localhost.tiangolo.com/docs |

Домен `*.localhost.tiangolo.com` указывает на `127.0.0.1` (как в `development.md`).

## 6. OSRM

Маршрутизация по-прежнему с хоста: `OSRM_BASE_URL=http://localhost:5000` в `.env` (Caddy её не проксирует).

## 7. Откат на HTTP

Уберите `VITE_CADDY_DEV` из `frontend/.env`, верните `VITE_API_URL=http://localhost:8000`, используйте `http://localhost:5173`.
