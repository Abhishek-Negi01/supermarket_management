# SuperMarket Pro - Inventory Management System

## Overview

A comprehensive Django-based inventory management system with QR code integration, real-time analytics, automated alerts, and integrated billing system.

## ✨ Key Features

### 🛒 Integrated Billing System

- **QR Code Scanning**: Fast checkout by scanning product QR codes
- **Manual Billing**: Traditional search and add products
- **Unified Workflow**: Mix QR scanning and manual entry in single bill
- **Real-Time Sync**: Scan on mobile, complete on desktop
- **Session-Based**: Each cashier has isolated bill session
- **Safe Stock Management**: Stock deducted only on bill completion
- **Receipt Generation**: Auto-generated bills with unique numbers (BILL-YYYYMMDD-XXXX)
- **PDF Export**: Download bills as PDF

### 🔐 Role-Based Access Control

- **CASHIER**: Billing, QR scanning, view own bills
- **STOCK KEEPER**: All cashier + product management, stock adjustments
- **MANAGER**: All cashier + analytics, reports, view all bills
- **ADMIN**: Full system access

### 📦 Product Management

- Product CRUD with categories and suppliers
- Stock tracking and adjustments
- Purchase order management
- QR code generation for products
- Bulk CSV import/export

### 📊 Analytics & Insights

- Real-time analytics dashboard with Chart.js
- Product velocity analysis (fast-moving products)
- Sales trends (7-day bar charts)
- Automated inventory alerts (low stock, out of stock)
- Email notifications for critical events
- Export reports (CSV, PDF)

### 💾 Data Management

- **Duplicate Prevention**: Unique constraints on critical fields
- **CSV Import/Export**: Bulk operations with templates
- **Atomic Transactions**: Safe operations with rollback
- **Data Validation**: Comprehensive error reporting

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
7. Billing by mobile: `cd d:\supermarket_management python manage.py runserver 0.0.0.0:8000`

## 🚀 Quick Start Guide

### For Cashiers (Billing)

#### Method 1: QR Scanning (Fast - 30 seconds)

```
1. Click "QR Scanner" in menu
2. Scan each product's QR code
3. Click "View Bill (X)" button
4. Select payment method (Cash/Card/UPI)
5. Click "Complete Bill"
6. Print receipt
```

#### Method 2: Manual Billing (Traditional - 60 seconds)

```
1. Click "Billing" in menu
2. Search product name
3. Click "+" to add
4. Repeat for all products
5. Select payment method
6. Click "Complete Bill"
7. Print receipt
```

#### Method 3: Mixed (Recommended - 40 seconds)

```
1. Open "Billing" page
2. Click "Scan QR" button
3. Scan products with QR codes
4. Return to Billing (auto-refreshes)
5. Manually add products without QR
6. Complete bill
7. Print receipt
```

### For Stock Keepers

```
1. Add/Edit products at /products/
2. Generate QR codes at /qr/generate/
3. Manage stock at /adjustments/
4. Record purchases at /purchases/
5. Import bulk data at /csv-import/
```

### For Managers

```
1. View analytics at /analytics/
2. Check reports at /reports/
3. Monitor alerts at /alerts/
4. View all bills at /bills/
5. Export data (CSV/PDF)
```

## 🔄 How QR Billing Integration Works

### Workflow

```
QR Scan → Add to Session → Billing Page (auto-refresh) → Complete Bill → Deduct Stock → Receipt
```

### Key Points

- ✅ QR scans add products to current bill session
- ✅ Billing page auto-refreshes every 2 seconds
- ✅ Stock validated on scan, deducted on completion
- ✅ Atomic transactions (all or nothing)
- ✅ Multi-device support (scan on mobile, complete on desktop)
- ✅ Each cashier has isolated session

### Session Structure

```python
request.session['current_bill'] = {
    "123": {  # Product ID
        "name": "Product A",
        "price": 50.00,
        "quantity": 2
    }
}
```

## 🔐 Role Setup

### Create User with Role

```
1. Admin Panel → Employees → Add Employee
   - Name, Email, Phone
   - Role: CASHIER/STOCK/MANAGER/ADMIN

2. Admin Panel → Users → Add User
   - Username, Password

3. Admin Panel → Employees → Edit Employee
   - Link User to Employee
   - Save
```

### Permission Matrix

| Feature           | Cashier | Stock Keeper | Manager | Admin |
| ----------------- | ------- | ------------ | ------- | ----- |
| Billing           | ✅      | ✅           | ✅      | ✅    |
| QR Scanning       | ✅      | ✅           | ✅      | ✅    |
| View Products     | ✅      | ✅           | ✅      | ✅    |
| Add/Edit Products | ❌      | ✅           | ❌      | ✅    |
| Stock Adjustments | ❌      | ✅           | ❌      | ✅    |
| Analytics         | ❌      | ❌           | ✅      | ✅    |
| Reports           | ❌      | ❌           | ✅      | ✅    |
| User Management   | ❌      | ❌           | ❌      | ✅    |

## 📡 API Endpoints

### Billing APIs

- `POST /api/scan_product/` - Scan QR and add to bill
- `POST /api/add-to-bill/` - Manually add product to bill
- `GET /api/get-bill/` - Get current bill items
- `POST /api/complete-bill/` - Complete bill and generate receipt
- `POST /api/remove-from-bill/` - Remove item from bill

### Other APIs

- `GET /api/verify_stock/` - Check stock levels
- `GET /api/analytics/` - Get analytics data
- `POST /api/trigger-alert-check/` - Manual alert check
- `GET /export/stock-csv/` - Export stock CSV
- `GET /export/analytics-pdf/` - Export analytics PDF

## Testing

Run tests with: `python manage.py test inventory`

## Management Commands

- `python manage.py check_alerts` - Run inventory alert checks
- `python manage.py collectstatic` - Collect static files for production

## 📥 CSV Import/Export

### Supported Types

1. **Categories** - Product categories
2. **Suppliers** - Supplier information
3. **Products** - Product catalog with pricing and stock
4. **Employees** - Staff members with roles
5. **Purchases** - Purchase orders (auto-updates stock)
6. **Stock Adjustments** - Stock corrections (auto-updates stock)

### Usage

```
1. Go to /csv-import/
2. Download template for data type
3. Fill template with data
4. Upload CSV file
5. Review results (created/updated/errors)
```

### Features

- ✅ Update existing or create new (no duplicates)
- ✅ Atomic transactions (rollback on error)
- ✅ Comprehensive error reporting
- ✅ Template downloads for correct format

## Production Deployment

1. Set `DEBUG = False` in settings
2. Configure proper email backend
3. Set up static file serving
4. Configure database for production
5. Set up automated alert scheduling

## Technology Stack

- **Backend**: Django 5.2, Python 3.8+
- **Database**: MySQL 8.0 (with unique constraints)
- **Frontend**: HTML5, TailwindCSS, JavaScript
- **Charts**: Chart.js
- **QR Codes**: qrcode library
- **PDF Generation**: xhtml2pdf
- **CSV Processing**: Python csv module
- **Authentication**: Django built-in auth

## 🎯 Common Scenarios

### Scenario 1: Fast Checkout (All QR)

```
Time: 30 seconds for 10 items
1. Open QR Scanner
2. Scan all products
3. View Bill
4. Complete
```

### Scenario 2: Mixed Checkout (QR + Manual)

```
Time: 40 seconds for 10 items
1. Open Billing page
2. Click "Scan QR"
3. Scan QR products
4. Return to Billing
5. Add non-QR products manually
6. Complete
```

### Scenario 3: Customer Changes Mind

```
1. Click "Remove" on item in bill
2. Stock NOT affected (only deducted on completion)
3. Continue with remaining items
```

### Scenario 4: Insufficient Stock

```
1. System shows error on scan/add
2. Item NOT added to bill
3. Check stock level
4. Adjust quantity or remove
```

## 🚨 Error Handling

| Error              | Cause                         | Solution                       |
| ------------------ | ----------------------------- | ------------------------------ |
| Insufficient Stock | Product stock < quantity      | Reduce quantity or remove item |
| Product Not Found  | Invalid QR or deleted product | Regenerate QR or add manually  |
| Connection Error   | Network issue                 | Check internet, refresh page   |
| No Items in Bill   | Empty bill completion         | Add at least one product       |

## 📊 Bill Number Format

**Format**: `BILL-YYYYMMDD-XXXX`

**Examples**:

- `BILL-20251112-0001` (First bill of Nov 12, 2025)
- `BILL-20251112-0002` (Second bill of same day)
- `BILL-20251113-0001` (First bill of next day)

**Note**: Counter resets daily

## 🔒 Data Integrity

### Unique Constraints

- Product names
- Category names
- Supplier names and emails
- Employee emails
- Bill numbers

### Stock Safety

- Stock validated on scan (early warning)
- Stock deducted only on bill completion (safe)
- Atomic transactions with `select_for_update()` (prevents race conditions)
- Rollback on any error (data consistency)

## 📈 Project Status

✅ **Core Inventory Management** - COMPLETE
✅ **QR Code Integration** - COMPLETE
✅ **Billing System** - COMPLETE
✅ **Role-Based Access Control** - COMPLETE
✅ **Analytics & Insights** - COMPLETE
✅ **CSV Import/Export** - COMPLETE

## 🎓 Training Time

- **Cashiers**: 5 minutes (QR scanning + billing)
- **Stock Keepers**: 15 minutes (product management + QR generation)
- **Managers**: 10 minutes (analytics + reports)
- **Admins**: 20 minutes (full system overview)

## 🛠️ Technology Stack

- **Backend**: Django 5.2, Python 3.8+
- **Database**: MySQL 8.0
- **Frontend**: HTML5, TailwindCSS, JavaScript
- **Charts**: Chart.js
- **QR Codes**: qrcode library
- **PDF**: xhtml2pdf
- **Authentication**: Django built-in auth


---

**Status**: ✅ Production Ready | **Version**: 1.0 | **Last Updated**: November 2025
