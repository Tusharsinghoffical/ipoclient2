# IPO Web Application

A comprehensive Django web application for tracking and managing Initial Public Offerings (IPOs). Built for Bluestock Fintech to provide real-time IPO information and market insights.

## Features

### 🚀 Core Features
- **IPO Tracking**: Monitor upcoming, ongoing, and listed IPOs
- **Real-time Data**: Live updates on IPO status and pricing
- **Search & Filter**: Advanced search and filtering capabilities
- **Responsive Design**: Modern, mobile-friendly interface
- **Admin Dashboard**: Comprehensive management interface

### 📊 IPO Information
- Company details and logos
- Price bands and issue sizes
- Important dates (open, close, listing)
- Performance metrics (listing gain, current returns)
- Document management (RHP, DRHP PDFs)

### 🔧 Technical Features
- **REST API**: Full API support for mobile apps
- **Admin Interface**: Django admin for data management
- **File Upload**: Support for images and PDF documents
- **Pagination**: Efficient data loading
- **SEO Optimized**: Search engine friendly

## Technology Stack

- **Backend**: Django 5.0.6
- **Frontend**: Bootstrap 5, Font Awesome
- **API**: Django REST Framework
- **Database**: PostgreSQL (configurable)
- **File Storage**: Local/Cloud storage support

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite for development)
- pip

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ipo-django
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Usage

### Web Interface
- **Homepage**: `/` - View all IPOs with filtering options
- **IPO Details**: `/ipo/<id>/` - Detailed IPO information
- **Admin Dashboard**: `/admin-dashboard/` - Management interface

### API Endpoints
- **All IPOs**: `GET /api/ipo/`
- **Filtered IPOs**: `GET /api/ipo/?status=upcoming`
- **Search IPOs**: `GET /api/ipo/?search=company_name`
- **Upcoming IPOs**: `GET /api/ipo/upcoming/`
- **Ongoing IPOs**: `GET /api/ipo/ongoing/`
- **Listed IPOs**: `GET /api/ipo/listed/`

### Admin Interface
- **Django Admin**: `/admin/` - Full CRUD operations
- **IPO Management**: Add, edit, delete IPOs
- **File Management**: Upload logos and documents

## Project Structure

```
ipo-django/
├── ipo_project/          # Main Django project
│   ├── settings.py       # Project settings
│   ├── urls.py          # Main URL configuration
│   └── wsgi.py          # WSGI configuration
├── ipo_app/             # IPO application
│   ├── models.py        # IPO data model
│   ├── views.py         # Views and API endpoints
│   ├── serializers.py   # API serializers
│   ├── admin.py         # Admin interface
│   └── urls.py          # App URL configuration
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   └── ipo_app/         # App-specific templates
├── media/               # Uploaded files
├── static/              # Static files
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Configuration

### Environment Variables
Create a `.env` file with the following variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://user:password@localhost:5432/ipo_db
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration
The application supports multiple database backends:

**SQLite (Development)**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**PostgreSQL (Production)**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ipo_db',
        'USER': 'ipo_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## API Documentation

### IPO Model Fields
- `company_name`: Company name
- `logo`: Company logo image
- `price_band`: IPO price range
- `open_date`: IPO opening date
- `close_date`: IPO closing date
- `issue_size`: Total issue size
- `issue_type`: Type of issue
- `listing_date`: Stock exchange listing date
- `status`: IPO status (upcoming/ongoing/listed)
- `ipo_price`: Final IPO price
- `listing_price`: Initial listing price
- `current_market_price`: Current market price
- `rhp_pdf`: Red Herring Prospectus
- `drhp_pdf`: Draft Red Herring Prospectus

### Calculated Fields
- `listing_gain`: Percentage gain on listing day
- `current_return`: Current return percentage

## Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure production database
- [ ] Set up static file serving
- [ ] Configure media file storage
- [ ] Set up SSL certificate
- [ ] Configure backup strategy
- [ ] Set up monitoring

### Docker Deployment
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
EXPOSE 8000
CMD ["gunicorn", "ipo_project.wsgi:application"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Email: support@bluestockfintech.com
- Documentation: [Link to docs]
- Issues: [GitHub Issues]

## Changelog

### v1.0.0 (2025-01-13)
- Initial release
- Basic IPO tracking functionality
- Admin interface
- REST API
- Responsive web interface

---