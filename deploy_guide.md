# Deployment Guide - SuperMarket Pro

## Local Network Deployment (LAN Access)

### 1. Update Settings
```python
# In settings.py
DEBUG = False
ALLOWED_HOSTS = ['*', 'your-ip-address', 'localhost']
```

### 2. Run Server
```bash
python manage.py runserver 0.0.0.0:8000
```
Access via: `http://YOUR-IP:8000`

## Production Deployment Options

### Option 1: PythonAnywhere (Free)
1. Upload project files
2. Set up MySQL database
3. Configure WSGI file
4. Set environment variables

### Option 2: Heroku (Free Tier Available)
1. Install Heroku CLI
2. Create `Procfile`: `web: gunicorn supermarket_management.wsgi`
3. Add `requirements.txt` dependencies
4. Deploy: `git push heroku main`

### Option 3: DigitalOcean/AWS
1. Set up Ubuntu server
2. Install Python, MySQL, Nginx
3. Configure Gunicorn + Nginx
4. Set up SSL certificate

## Required Changes for Production

### 1. Database (Use PostgreSQL/MySQL)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 2. Static Files
```bash
python manage.py collectstatic
```

### 3. Security Settings
```python
DEBUG = False
SECRET_KEY = 'your-production-secret-key'
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
```

## Quick Local Network Setup
1. Find your IP: `ipconfig` (Windows) or `ifconfig` (Linux/Mac)
2. Run: `python manage.py runserver 0.0.0.0:8000`
3. Access from any device: `http://YOUR-IP:8000`