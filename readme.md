# Sweet URL

Sweet URL is a modern full-stack URL shortener built with FastAPI, PostgreSQL, Redis, Docker, and Google OAuth authentication.

It allows authenticated users to create shortened links, generate QR codes, track analytics, manage URLs from a dashboard, and configure expiration times.


# Features

* Google OAuth Authentication
* Secure session-based login
* URL shortening with custom aliases
* QR code generation
* Redis caching for fast redirects
* Click analytics tracking
* Expiration support (1h / 24h / 7d)
* User dashboard
* Copy-to-clipboard support
* Delete URLs
* Responsive modern UI
* Dockerized setup


# Tech Stack

## Backend

* FastAPI
* SQLAlchemy
* PostgreSQL
* Redis
* Authlib

## Frontend

* HTML
* TailwindCSS
* Vanilla JavaScript
* Jinja2 Templates

## DevOps

* Docker
* Docker Compose


## Project Structure

```bash
sweet-url/
│
├── app/
│   ├── db/
│   │   ├── database.py
│   │   └── redis_client.py
│   │
│   ├── models/
│   │   ├── unused_key.py
│   │   ├── url.py
│   │   └── user.py
│   │
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── dashboard_routes.py
│   │   └── url_routes.py
│   │
│   ├── schemas/
│   │   └── url.py
│   │
│   ├── services/
│   │   └── url_service.py
│   │
│   ├── utils/
│   │   ├── dependencies.py
│   │   └── security.py
│   │
│   ├── __init__.py
│   └── main.py
│
├── scripts/
│
├── static/
│   ├── qr/
│   └── favicon.ico
│
├── templates/
│   ├── dashboard.html
│   └── index.html
│
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── README.md
└── requirements.txt
```


## Environment Variables

Create a .env file:
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/sweeturl

REDIS_URL=redis://cache:6379

GOOGLE_CLIENT_ID=your_google_client_id

GOOGLE_CLIENT_SECRET=your_google_client_secret

SECRET_KEY=your_secret_key

BASE_URL=http://localhost:8000
``` 
## Start Application

```bash
docker compose up --build
```


## Stop Containers

```bash
docker compose down
```


# Dashboard Features

Authenticated users can:

* View all created URLs
* Track click counts
* See expiration times
* Copy short links
* Delete URLs
* Access QR codes


# Redis Caching

Redirects are cached using Redis for faster resolution and reduced database load.


# Analytics

Each redirect increments a click counter stored in PostgreSQL.


# Timezone Handling

Timestamps are stored in UTC and automatically converted to the user's local browser timezone in the dashboard.


# Future Improvements

* Custom domains
* Public analytics pages
* Rate limiting
* Link editing
* Pagination
* Advanced charts
* Team workspaces
* API keys
* Background analytics jobs


## Contributors
* [b-harsha-v](https://github.com/b-harsha-v)
* [prav-kotte1](https://github.com/prav-kotte1)

