# Сервис автоматизации распределения задач для выездных сотрудников банка
<img width="261" height="610" alt="image" src="https://github.com/user-attachments/assets/0575744b-b198-4369-9956-3eb938145938" />
<img width="261" height="610" alt="image" src="https://github.com/user-attachments/assets/68ff2c65-6d3a-4e81-b981-1278b21c3c2f" />
<img width="1048" height="725" alt="image" src="https://github.com/user-attachments/assets/6d4b4c0d-f817-46c1-9bcc-577b9b770583" />

# Видео Демонстрация решения
https://github.com/user-attachments/assets/7b1d8e6d-5c2c-4149-99de-611b548a6e6e

# Краткое описание
Веб-сервис для Совкомбанка: 3 типа задач, 8 сотрудников, 43 агентские точки Краснодара. Backend - FastAPI и PostgreSQL, маршруты - OR-Tools и OSRM, frontend - React с картой для выездного. На датасете ТЗ: 19 задач назначено, 10 перенесено, время распределения - менее секунды. Менеджер видит отчёт и диаграммы, сотрудник - маршрут и статусы задач.

# Актуальность
- ООО «Совкомбанк Технологии» выдвинул задачу создания веб-сервиса распределения задач на хакатоне. Компания предоставила техническое задание и датасет.
- Датасет Краснодара содержит 43 агентские точки, 8 сотрудников
- В исследовании Solano-Charris и соавторов По сравнению с ручным планированием маршрутов веб-сервис позволяет сократить общее время в пути, повышая операционную производительность на 22%.

# Выбор моделей или методик для решения
<img width="1243" height="550" alt="image" src="https://github.com/user-attachments/assets/761e48f6-4f89-4d7d-a311-6fbf428631ba" />

# UML Диаграмма последовательности для распределения задач
<img width="1110" height="656" alt="image" src="https://github.com/user-attachments/assets/7452fef8-b9bc-4eab-892c-45249b7b9569" />

# Стек
<img width="1282" height="567" alt="image" src="https://github.com/user-attachments/assets/a023e0c3-c7c3-4150-967a-737c99c59daa" />

# Схема баз данных в нотации Мартина
<img width="1223" height="691" alt="image" src="https://github.com/user-attachments/assets/5a17fcc1-d409-440a-815a-6f27eae2ba7e" />

# Контекстная диаграмма IDEF0
<img width="1190" height="660" alt="image" src="https://github.com/user-attachments/assets/413967c5-5689-4d85-b54e-78e509e6e0e8" />

# Декомпозиция процесса А0: “Распределить задачи для выездных сотрудников банка” 
<img width="1182" height="653" alt="image" src="https://github.com/user-attachments/assets/ed54d8ad-20a6-443d-a9cc-9f8f8ae7908a" />

# Анализ сложности Big O
<img width="1263" height="561" alt="image" src="https://github.com/user-attachments/assets/8832cb33-fa0e-4694-b2cb-5d901c86c7da" />



#
Скачать .pbf.osm с геофабрик
преобразовать в .pmtiles
скачать node js
tileserver-gl --file a.pmtiles для запуска сервера с тайтлами

## Поднятие локального osrm

1. Скачайте нужный регион, например, Москву и область:

bash
wget https://download.geofabrik.de/russia/central-fed-district-latest.osm.pbf -O data/map.pbf

2. Извлечение данных (Extract): Конвертируем PBF во внутренний формат OSRM.

bash
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/map.pbf

3. Нарезка (Partition): Оптимизируем граф для быстрого поиска.

bash
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/map.osrm

4. Настройка (Customize): Рассчитываем метрики (веса дорог).

bash
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/map.osrm

5. Запуск сервера (Routed): Поднимаем API сервер. Флаг -d оставит его работать в фоне.

bash
docker run -d -p 5000:5000 --rm --name osrm -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/map.osrm

Проверка работоспособности 

http://localhost:5000/route/v1/driving/38.975313,45.035470;39.033889,45.118611?steps=true

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
  - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) for the Python SQL database interactions (ORM).
  - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
  - 💾 [PostgreSQL](https://www.postgresql.org) as the SQL database.
- 🚀 [React](https://react.dev) for the frontend.
  - 💃 Using TypeScript, hooks, [Vite](https://vitejs.dev), and other parts of a modern frontend stack.
  - 🎨 [Tailwind CSS](https://tailwindcss.com) and [shadcn/ui](https://ui.shadcn.com) for the frontend components.
  - 🤖 An automatically generated frontend client.
  - 🧪 [Playwright](https://playwright.dev) for End-to-End testing.
  - 🦇 Dark mode support.
- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- 🔒 Secure password hashing by default.
- 🔑 JWT (JSON Web Token) authentication.
- 🚢 Deployment instructions using Docker Compose.

### Configure

You can then update configs in the `.env` files to customize your configurations.

Before deploying it, make sure you change at least the values for:

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`

You can (and should) pass these as environment variables from secrets.

Read the [deployment.md](./deployment.md) docs for more details.

## Backend Development

Backend docs: [backend/README.md](./backend/README.md).

## Frontend Development

Frontend docs: [frontend/README.md](./frontend/README.md).

## Deployment

Deployment docs: [deployment.md](./deployment.md).

## Development

General development docs: [development.md](./development.md).

This includes using Docker Compose, custom local domains, `.env` configurations, etc.

## Release Notes

Check the file [release-notes.md](./release-notes.md).

## License

The Full Stack FastAPI Template is licensed under the terms of the MIT license.


