# Placement Predictor System

A comprehensive web-based placement management system that helps colleges manage student placements, predict employability, and provide AI-powered recommendations.

## Features

### For Students
- Track academic performance and skill levels
- Take auto-generated quizzes based on uploaded syllabi
- View employability predictions
- Enroll in training sessions
- Access personalized recommendations
- Download placement certificates

### For TPO (Training & Placement Officer)
- Manage student records
- Generate AI-powered recommendations
- Create and manage training sessions
- View analytics and reports
- Run what-if simulations
- Export data in various formats

### For College Administrators
- Department-wise analytics
- Company recruitment tracking
- Student performance reports
- Custom report generation
- Bulk student data import
 - Personalized recommendations

### **ML Model**
- Random Forest Classifier
- 95.55% accuracy
- 0.9909 ROC-AUC score

### **Database**
- SQLite backend
- Full CRUD operations
- Django Admin panel

## Quick Start

### 1. Configure Environment Variables (Required)

```bash
# Copy the example file
Copy-Item .env.example .env

# Edit .env and add your credentials
# See SECURITY_SETUP.md for detailed instructions
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Create Sample Data
```bash
python create_sample_data.py
```

### 5. Start Server
```bash
python manage.py runserver
```

### 6. Access Application
- **Main Site:** http://127.0.0.1:8000/
- **Django Admin:** http://127.0.0.1:8000/admin/
- **College Portal:** http://127.0.0.1:8000/college/login/
- **Placement Portal:** http://127.0.0.1:8000/placement/login/

## Login Credentials

**Demo/Development Credentials:**

| Portal | Username | Password |
|--------|----------|----------|
| Django Admin | admin | admin123 |
| College Portal | college | college123 |
| Placement Portal | placement | placement123 |

**Note:** Change these passwords in production environments.

## Project Structure

```
Placement Predictor/
 predictor/ # Main Django app
 placement_project/ # Django settings
 models/ # ML model files
 data/ # Datasets
 static/ # CSS, JS, images
 media/ # User uploads
 db.sqlite3 # Database
 manage.py # Django CLI
```

## Documentation

- **SECURITY_SETUP.md** - **START HERE** - API keys and credentials setup
- **docs/SETUP_GUIDE.md** - Complete installation guide
- **docs/ENV_SETUP.md** - Environment variables configuration
- **docs/DATABASE_ACCESS_GUIDE.md** - Database access methods
- **docs/DATABASE_MANAGEMENT.md** - CRUD operations guide
- **docs/GEMINI_QUIZ_INTEGRATION.md** - AI quiz generation setup
- **docs/GOOGLE_SEARCH_API_SETUP.md** - Optional search API setup

## VTU Grading System

| Grade | Marks | Points |
|-------|-------|--------|
| S | 135-150 | 10.0 |
| A | 120-134 | 9.0 |
| B | 105-119 | 8.0 |
| C | 90-104 | 7.0 |
| D | 75-89 | 6.0 |
| E | 60-74 | 5.0 |
| F | 0-59 | 0.0 |

## Utilities

- `check_db.py` - Check database
- `create_sample_data.py` - Generate sample data
- `set_admin_password.py` - Reset admin password

---

**Built with Django 5.2.7 + Python 3.13 + SQLite**
