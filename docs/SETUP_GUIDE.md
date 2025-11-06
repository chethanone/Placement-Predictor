# Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/chethanone/Placement-Predictor.git
cd Placement-Predictor
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edit `.env` and add your API keys. See [SECURITY_SETUP.md](../SECURITY_SETUP.md) for details.

### 5. Run Database Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 7. Load Sample Data (Optional)

```bash
python create_sample_data.py
```

### 8. Start Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Application URLs

- **Main Site:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **College Portal:** http://127.0.0.1:8000/college/login/
- **Placement Portal:** http://127.0.0.1:8000/placement/login/
- **Student Portal:** http://127.0.0.1:8000/student/

## Default Credentials (Development)

| Portal | Username | Password |
|--------|----------|----------|
| Admin Panel | admin | admin123 |
| College Portal | college | college123 |
| Placement Portal | placement | placement123 |

**Important:** Change these credentials before deploying to production.

## Features

### Student Portal
- Placement prediction based on academic performance
- AI-powered quiz system
- Upload PDF/PPT files for automated quiz generation
- View prediction results and recommendations

### College Portal
- Student management (CRUD operations)
- Subject management
- VTU-style marks entry system
- Automatic CGPA calculation
- Analytics and reports

### Placement Portal
- Training session management
- Student performance analytics
- Personalized career recommendations
- Department-wise analysis

## Troubleshooting

### Database Issues
```bash
python manage.py flush  # Clear database
python manage.py migrate  # Re-run migrations
```

### Static Files Not Loading
```bash
python manage.py collectstatic
```

### Port Already in Use
```bash
python manage.py runserver 8080  # Use different port
```

## Documentation

- [Security Setup](../SECURITY_SETUP.md) - API keys and credentials configuration
- [Database Management](DATABASE_MANAGEMENT.md) - Database operations guide
- [Gemini Integration](GEMINI_QUIZ_INTEGRATION.md) - AI quiz generation setup
- [Google Search API](GOOGLE_SEARCH_API_SETUP.md) - Optional search API configuration

## Support

For issues or questions, please open an issue on GitHub.
