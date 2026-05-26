# SiteMap Django Project

A simple Django project for extracting or working with sitemap-related data.

## Project structure

- `manage.py` - Django management script
- `sitemap/` - Django project settings and URL configuration
- `extractor/` - app containing models, views, serializers, and services
- `db.sqlite3` - local SQLite database file

## Setup

1. Create and activate a Python virtual environment (recommended):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```


## Run the project

From the project root:

```powershell
python manage.py runserver
```

Then open the browser at `http://127.0.0.1:8000/`.

## Useful commands

- `python manage.py makemigrations` — create database migrations
- `python manage.py migrate` — apply migrations
- `python manage.py createsuperuser` — create an admin user

## Notes

- The main Django app is `extractor`.
- The project settings are in `sitemap/settings.py`.
- This is a lightweight local project; use the virtual environment to keep dependencies separate.
