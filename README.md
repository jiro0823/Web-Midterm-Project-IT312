# Web Midterm Project (IT312)

A Django web application built as a midterm project for IT312. The project provides user authentication (including social login via Google and Facebook using `django-allauth`), a dashboard, and a variety of utility pages (QR, cipher, jokes, etc.).

## Table of Contents

- Project status
- Features
- Requirements
- Quick start
- Environment variables and secrets
- Security and secrets handling (IMPORTANT)
- Deployment notes
- Development and contribution
- License

## Project status

- Development mode: DEBUG=True in the repository's development settings. Do not enable DEBUG in production.
- The repository had secrets in `midterm_project/settings.py` which have been removed from history. If you previously cloned the repo, re-clone or reset your local copy as described below.

## Features

- Custom user model (`accounts.CustomUser`)
- Django admin integrated
- Social login with Google and Facebook via `django-allauth`
- Utility pages: QR generation/reading, cipher tools, joke API integration, etc.

## Requirements

- Python 3.11+ (project uses venv)
- Django 5.2.x
- Other Python dependencies listed in `requirements.txt` (if present). If not, install from `pip install -r requirements.txt`.

## Quick start (development)

1. Clone the repository:

   git clone https://github.com/jiro0823/Web-Midterm-Project-IT312.git
   cd Web-Midterm-Project-IT312

2. Create and activate a virtual environment (Windows PowerShell):

   python -m venv venv
   .\venv\Scripts\Activate.ps1

3. Install dependencies:

   pip install -r requirements.txt

4. Create a `.env` file (recommended) or set environment variables as described below.

5. Apply migrations and create a superuser:

   python manage.py migrate
   python manage.py createsuperuser

6. Run the development server:

   python manage.py runserver

7. Open `http://localhost:8000` in your browser.

## Environment variables and secrets

This project uses social authentication credentials for Google and Facebook. Do not store credentials in `settings.py` or commit them to Git.

Recommended approach: store secrets in environment variables and load them in `midterm_project/settings.py` (example using `os.getenv` or `python-dotenv`). Example env variables:

- `DJANGO_SECRET_KEY` — Django SECRET_KEY
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `FACEBOOK_CLIENT_ID`
- `FACEBOOK_CLIENT_SECRET`

Example snippet (in `settings.py`):

```python
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        }
    },
    'facebook': {
        'APP': {
            'client_id': os.getenv('FACEBOOK_CLIENT_ID'),
            'secret': os.getenv('FACEBOOK_CLIENT_SECRET'),
        }
    }
}
