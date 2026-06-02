# Sitemap Extractor API

A Django REST API that extracts URLs from XML sitemaps asynchronously using Celery and Redis.

## Features

* Extract URLs from XML sitemaps
* Supports sitemap indexes and nested sitemaps
* Asynchronous processing with Celery
* Redis-based task queue and caching
* Task status polling
* Guest and authenticated user support
* Pagination for large sitemap results
* Database persistence of extraction results
* Automatic expiration of stored results

---

## Tech Stack

* Django
* Django REST Framework
* Celery
* Redis
* SQLite (Development)
* Docker (Optional)

---

## Project Structure

```text
project/
│
├── sitemap/
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
│
├── tools/
│   └── backlinkGap/
│       └── sitemap_extractor/
│           ├── models.py
│           ├── views.py
│           ├── services.py
│           ├── tasks.py
│           ├── serializers.py
│           └── urls.py
│
├── manage.py
└── requirements.txt
```

---

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd <project-name>
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Virtual Environment

#### Windows

```bash
.venv\Scripts\activate
```

#### Linux / Mac

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key

DEBUG=True

REDIS_URL=redis://localhost:6379/0
```

---

## Database Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Running Redis

### Docker

```bash
docker run -d --name redis -p 6379:6379 redis
```

Verify:

```bash
docker ps
```

---

## Running Django

```bash
python manage.py runserver
```

Application:

```text
http://127.0.0.1:8000/
```

---

## Running Celery Worker

### Linux / Mac

```bash
celery -A sitemap worker -l info
```

### Windows

```bash
celery -A sitemap worker -l info --pool=solo
```

---

## API Endpoints

### Start Sitemap Extraction

```http
POST /api/sitemap-extractor/
```

Request:

```json
{
  "url": "https://example.com"
}
```

Response:

```json
{
  "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "status": "processing"
}
```

---

### Check Task Status

```http
GET /api/sitemap-task/<task_id>/
```

Possible responses:

```json
{
  "status": "PENDING"
}
```

```json
{
  "status": "STARTED"
}
```

```json
{
  "status": "FAILURE",
  "error": "Error message"
}
```

---

### Get Paginated Results

```http
GET /api/sitemap-task/<task_id>/?page=1
```

Response:

```json
{
  "status": "SUCCESS",
  "count": 2500,
  "page": 1,
  "page_size": 100,
  "total_pages": 25,
  "results": [
    "https://example.com/page-1",
    "https://example.com/page-2"
  ]
}
```

---

## Guest vs Authenticated Users

### Guest Users

* Maximum URLs: 1,000
* Cached responses supported

### Authenticated Users

* Maximum URLs: 100,000
* Results stored and reused until expiration

---

## Caching

Guest user results are cached in Redis:

```text
sitemap:<domain>
```

Cache timeout:

```text
1 hour
```

---

## Database Storage

Each extraction stores:

* User ID
* IP Address
* Domain
* Extracted URLs
* Total URL Count
* Status
* Creation Timestamp
* Expiration Timestamp

Statuses:

```text
pending
completed
failed
```

---

## Development Notes

### Restart Celery Worker After Task Changes

```bash
docker restart <celery-container>
```

or

```bash
celery -A sitemap worker -P threads -c 8 -l info  
```

### Remove pending tasks from celery

```bash
celery -A sitemap purge  
```



## Future Improvements

* Celery Beat cleanup task
* Rate limiting
* Export results as CSV
* Monitoring and metrics

---
