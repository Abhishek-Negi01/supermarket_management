# SuperMarket Pro - Inventory Management System

## Overview
A comprehensive Django-based inventory management system with QR code integration, real-time analytics, and automated alerts.

## Features

### Phase 1: Core Inventory Management
- Product management with categories and suppliers
- Stock tracking and adjustments
- Purchase order management
- User authentication and role-based access

### Phase 2: QR Code Integration
- QR code generation for products
- Mobile-friendly QR scanning interface
- Automated stock updates via scanning
- Scan event logging and history

### Phase 3: Analytics & Automated Insights
- Real-time analytics dashboard with Chart.js
- Product velocity analysis and fast-moving product identification
- Automated inventory alerts (low stock, out of stock, fast moving)
- Email notifications for critical inventory events
- Report exports (CSV, PDF)
- System-wide notifications center

## Installation

### Prerequisites
- Python 3.8+
- MySQL 8.0+
- Django 5.2+

### Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure database in `settings.py`
4. Run migrations: `python manage.py migrate`
5. Create superuser: `python manage.py createsuperuser`
6. Start server: `python manage.py runserver`

## Usage

### QR Code Workflow
1. Generate QR codes for products via Admin panel
2. Use mobile scanner at `/qr/scan/` for billing
3. Automatic stock deduction and event logging
4. View scan history and analytics

### Analytics Dashboard
- Access at `/analytics/` for comprehensive insights
- Monitor product velocity and stock health
- Receive automated alerts for inventory issues
- Export reports for external analysis

### Alert System
- Automated hourly alert checks
- Email notifications for critical events
- Manual alert triggers via dashboard
- Alert management and dismissal interface

## API Endpoints

### Product Management
- `POST /api/scan_product/` - Scan QR code and update stock
- `GET /api/verify_stock/` - Check current stock levels
- `POST /api/add_to_cart/` - Add products to cart

### Analytics
- `GET /api/analytics/` - Get analytics data
- `POST /api/trigger-alert-check/` - Manual alert check
- `POST /api/mark-notification-read/` - Mark notifications as read

### Exports
- `GET /export/stock-csv/` - Export stock report as CSV
- `GET /export/analytics-pdf/` - Export analytics report as PDF

## Testing
Run tests with: `python manage.py test inventory`

## Management Commands
- `python manage.py check_alerts` - Run inventory alert checks
- `python manage.py collectstatic` - Collect static files for production

## Production Deployment
1. Set `DEBUG = False` in settings
2. Configure proper email backend
3. Set up static file serving
4. Configure database for production
5. Set up automated alert scheduling

## Technology Stack
- **Backend**: Django 5.2, Python 3.8+
- **Database**: MySQL 8.0
- **Frontend**: HTML5, TailwindCSS, JavaScript
- **Charts**: Chart.js
- **QR Codes**: qrcode library
- **PDF Generation**: xhtml2pdf
- **Authentication**: Django built-in auth

## License
MIT License