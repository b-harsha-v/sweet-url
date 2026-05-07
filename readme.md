# Sweet URL

A scalable URL shortening service built with FastAPI, PostgreSQL, Redis, and Docker.

## Live Demo

https://sweet-url.duckdns.org/


## Features

- URL shortening with unique aliases
- Custom alias support
- QR code generation for shortened URLs
- Redis caching for fast redirects
- Expiring URLs
- PostgreSQL persistence
- Dockerized deployment
- Automatic cache warming
- Alias validation and normalization


## Tech Stack

- FastAPI
- PostgreSQL
- Redis
- SQLAlchemy (Async)
- Docker & Docker Compose
- Jinja2 Templates
- QRCode (Python)

## Project Structure

```text
app/
├── db/
│   ├── database.py
│   └── redis_client.py
├── models/
│   ├── url.py
│   └── unused_key.py
├── main.py
templates/
static/ 
└── qr/
docker-compose.yml
Dockerfile
requirements.txt
````

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/sweet-url.git
cd sweet-url
```


## Local Setup
```bash
docker compose up --build
```

## Contributing

Contributions are welcome. Please open issues or pull requests for bug fixes and improvements.


## Future Improvements

* Analytics dashboard
* Click tracking
* Rate limiting
* User authentication
* Distributed key generation service
* Monitoring and observability