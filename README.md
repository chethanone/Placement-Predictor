# AI Placement Predictor System

A comprehensive Django-based placement prediction system with Machine Learning for colleges.

## Features

### **3-Portal Architecture**
1. **Student Portal** - No login required
 - Placement prediction
 - Quiz system (upload PDF/PPT)
 - View results

2. **College Portal** - Secure login
 - Student management (CRUD)
 - Subject management (CRUD)
 - VTU-style marks entry
 - Auto CGPA calculation

3. **Placement Portal** - Secure login
 - Training session management
 - Student analytics
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

### 1. Configure Environment Variables ⚠️
**IMPORTANT:** Set up your API keys first!
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

⚠️ **Change these passwords in production!**

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

- **SECURITY_SETUP.md** - ⚠️ **START HERE** - API keys and credentials setup
- **ENV_SETUP.md** - Environment variables configuration
- **DATABASE_ACCESS_GUIDE.md** - Database access methods
- **DATABASE_MANAGEMENT.md** - CRUD operations guide
- **GEMINI_QUIZ_INTEGRATION.md** - AI quiz generation setup
- **GOOGLE_SEARCH_API_SETUP.md** - Optional search API setup

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
