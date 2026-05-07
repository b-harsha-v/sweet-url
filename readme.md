# Sweet URL

A scalable URL shortening service built with FastAPI, PostgreSQL, Redis, and Docker.

## Live Demo

http://13.49.49.151:8000/


## Features

- URL shortening with unique aliases
- Custom alias support
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
git clone sweet-url
cd sweet-url
docker compose up --build
```

## Contributing

Contributions are welcome. Please open issues or pull requests for bug fixes and improvements.


## Future Improvements

* Analytics dashboard
* Click tracking
* Rate limiting
* User authentication
* QR code generation
* Distributed key generation service
* Monitoring and observability