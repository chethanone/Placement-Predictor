# HOW TO ACCESS THE DATABASE

## **Database File Location:**
```
C:\Placement Predictor\db.sqlite3
```

---

## **5 WAYS TO ACCESS THE DATABASE:**

### **1. Django Admin Panel (EASIEST & RECOMMENDED)**

**Access URL:** http://127.0.0.1:8000/admin/

**Credentials:**
- Username: `admin`
- Password: `admin123`

**What You Can Do:**
- View all tables in a beautiful UI
- Add, Edit, Delete any record
- Search and filter data
- Bulk operations
- View relationships between tables
- Export data

**Steps:**
1. Make sure server is running: `venv\Scripts\python.exe manage.py runserver`
2. Open browser: http://127.0.0.1:8000/admin/
3. Login with admin/admin123
4. You'll see all tables:
- Student records
- Subjects
- Student marks
- Quizzes
- Predictions
- Training sessions
- Recommendations

---

### **2. Through Your Application Portals**

#### **College Portal** (http://127.0.0.1:8000/college/login/)
- Username: `college`
- Password: `college123`
- **Access:** Students, Subjects, Marks

#### **Placement Portal** (http://127.0.0.1:8000/placement/login/)
- Username: `placement`
- Password: `placement123`
- **Access:** Training Sessions, Analytics, Recommendations

---

### **3. Using Python Script** (Programmatic Access)

Create a file `query_db.py`:
```python
import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Example: Get all students
cursor.execute("SELECT * FROM predictor_studentrecord")
students = cursor.fetchall()
for student in students:
print(student)

# Example: Get subjects
cursor.execute("SELECT * FROM predictor_subject")
subjects = cursor.fetchall()
for subject in subjects:
print(subject)

conn.close()
```

Run: `venv\Scripts\python.exe query_db.py`

---

### **4. Using DB Browser for SQLite** (GUI Tool)

**Download:** https://sqlitebrowser.org/

**Steps:**
1. Download and install DB Browser for SQLite
2. Open the application
3. Click "Open Database"
4. Navigate to: `C:\Placement Predictor\db.sqlite3`
5. You can now:
- Browse all tables
- Execute SQL queries
- Edit data directly
- Export to CSV/JSON
- View database schema

---

### **5. Using VS Code Extension**

**Extension:** SQLite Viewer

**Steps:**
1. Install "SQLite Viewer" extension in VS Code
2. Open workspace: `C:\Placement Predictor`
3. Right-click `db.sqlite3` → "Open Database"
4. View and query data directly in VS Code

---

## **Database Tables:**

| Table Name | Description | Records |
|------------|-------------|---------|
| `predictor_studentrecord` | Student information | 6 |
| `predictor_subject` | Subjects/Courses | 6 |
| `predictor_studentmarks` | VTU marks entries | 0 |
| `predictor_studentquiz` | Quiz records | 0 |
| `predictor_quizquestion` | Quiz questions | 0 |
| `predictor_studentprediction` | Placement predictions | 6 |
| `predictor_trainingsession` | Training sessions | 6 |
| `predictor_sessionrecommendation` | Session recommendations | 0 |
| `auth_user` | Django users (admin, college, placement) | 3 |

---

## **Quick Check Script**

Already created: `check_db.py`

Run this anytime:
```bash
venv\Scripts\python.exe check_db.py
```

Shows:
- All tables
- Record counts
- Sample data

---

## **RECOMMENDED FOR YOU:**

### **For Viewing & Managing Data:**
**Use Django Admin** (http://127.0.0.1:8000/admin/)
- Most user-friendly
- No SQL knowledge needed
- Beautiful interface
- Safe operations with confirmations

### **For Advanced SQL Queries:**
**Use DB Browser for SQLite**
- Full SQL capabilities
- Visual query builder
- Export features
- Schema visualization

### **For Quick Checks:**
**Use check_db.py script**
- Fast terminal output
- No browser needed
- Easy automation

---

## **Common Operations:**

### **View All Students:**
**Django Admin:** http://127.0.0.1:8000/admin/predictor/studentrecord/

**SQL:**
```sql
SELECT * FROM predictor_studentrecord;
```

### **View All Marks:**
**Django Admin:** http://127.0.0.1:8000/admin/predictor/studentmarks/

**SQL:**
```sql
SELECT * FROM predictor_studentmarks;
```

### **View Training Sessions:**
**Django Admin:** http://127.0.0.1:8000/admin/predictor/trainingsession/

**SQL:**
```sql
SELECT * FROM predictor_trainingsession;
```

---

## **All Access Credentials:**

| Portal | Username | Password | URL |
|--------|----------|----------|-----|
| **Django Admin** | admin | admin123 | /admin/ |
| **College Portal** | college | college123 | /college/login/ |
| **Placement Portal** | placement | placement123 | /placement/login/ |

---

## **Backup Database:**

```powershell
# Create backup
Copy-Item "db.sqlite3" "db_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sqlite3"
```

---

## **Important Notes:**

1. **Django Admin** is the SAFEST way - it respects all model validations
2. Direct SQL edits bypass Django validations - use with caution
3. Always backup before bulk operations
4. The database file is locked when server is running
5. All changes through any method are immediately saved

---

## **Getting Started:**

**Right Now, Try This:**

1. Make sure server is running:
```bash
cd "C:\Placement Predictor"
venv\Scripts\python.exe manage.py runserver
```

2. Open browser: http://127.0.0.1:8000/admin/

3. Login: admin / admin123

4. Click "Student records" to see all students

5. Click any student to edit

6. Try adding a new student!

**You now have FULL database access!**
