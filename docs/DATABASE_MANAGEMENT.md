# SQLite DATABASE MANAGEMENT - COMPLETE GUIDE

## DATABASE CONFIGURATION

**Backend:** SQLite
**Database File:** `db.sqlite3`
**Location:** `C:\Placement Predictor\db.sqlite3`
**Status:** Active and Working

---

## DATABASE TABLES

All data is stored in SQLite with the following tables:

### Core Tables
- `predictor_studentrecord` - Student information (6 students)
- `predictor_subject` - Subjects/Courses (6 subjects)
- `predictor_studentmarks` - VTU-style marks entries
- `predictor_studentquiz` - Quiz records
- `predictor_quizquestion` - Individual quiz questions
- `predictor_studentprediction` - Placement predictions (6 records)
- `predictor_trainingsession` - Training sessions (6 sessions)
- `predictor_trainingsession_registered_students` - Session registrations
- `predictor_sessionrecommendation` - Personalized recommendations

---

## COMPLETE CRUD OPERATIONS

### COLLEGE PORTAL

#### **STUDENT MANAGEMENT**
| Operation | URL | Description |
|-----------|-----|-------------|
| **CREATE** | `/college/student/add/` | Add new student with VTU USN |
| **READ** | `/college/students/` | View all students with filters |
| **UPDATE** | `/college/student/<id>/edit/` | Edit student details |
| **DELETE** | `/college/student/<id>/delete/` | Delete student (with confirmation) |
| **MARKS** | `/college/student/<id>/marks/` | Enter VTU marks (Internal + External) |

**Fields Managed:**
- Student ID (VTU USN format)
- Name, Email, Phone
- Branch (CSE/ISE/ECE/ME/CE/EEE)
- Current Semester (1-8)
- Batch Year
- CGPA (auto-calculated)
- Total Backlogs (auto-counted)

#### **SUBJECT MANAGEMENT**
| Operation | URL | Description |
|-----------|-----|-------------|
| **CREATE** | `/college/subject/add/` | Add new subject |
| **READ** | `/college/subjects/` | View all subjects with filters |
| **UPDATE** | `/college/subject/<id>/edit/` | Edit subject details |
| **DELETE** | `/college/subject/<id>/delete/` | Delete subject (with confirmation) |

**Fields Managed:**
- Subject Code (e.g., CS301)
- Subject Name
- Branch
- Semester (1-8)
- Credits (1-6)

#### **MARKS ENTRY (VTU-Style)**
| Operation | URL | Description |
|-----------|-----|-------------|
| **CREATE** | `/college/student/<id>/marks/` | Enter marks for a subject |
| **UPDATE** | `/college/student/<id>/marks/` | Update existing marks |

**Auto-Calculations:**
- Total Marks = Internal (max 50) + External (max 100)
- Grade Assignment (S/A/B/C/D/E/F)
- Grade Points (10/9/8/7/6/5/0)
- Backlog Detection (marks < 60)
- CGPA Recalculation (weighted average)

**VTU Grading Scale:**
- S: 135-150 (10.0)
- A: 120-134 (9.0)
- B: 105-119 (8.0)
- C: 90-104 (7.0)
- D: 75-89 (6.0)
- E: 60-74 (5.0)
- F: 0-59 (0.0) - **BACKLOG**

---

### PLACEMENT PORTAL

#### **TRAINING SESSION MANAGEMENT**
| Operation | URL | Description |
|-----------|-----|-------------|
| **CREATE** | `/placement/session/add/` | Create new training session |
| **READ** | `/placement/sessions/` | View all sessions with filters |
| **UPDATE** | `/placement/session/<id>/edit/` | Edit session details |
| **DELETE** | `/placement/session/<id>/delete/` | Delete session (with confirmation) |

**Fields Managed:**
- Title & Description
- Session Type (Technical/Aptitude/Communication/Interview/GD/Resume)
- Scheduled Date & Time
- Duration (minutes)
- Venue
- Max Students Capacity
- Resource Links
- Active Status

#### **STUDENT RECOMMENDATIONS**
| Operation | URL | Description |
|-----------|-----|-------------|
| **CREATE** | `/placement/student/<id>/recommend/` | Recommend session to student |
| **READ** | `/placement/student/<id>/` | View student profile & recommendations |

**Fields Managed:**
- Student selection
- Training session selection
- Recommendation reason
- Priority (High/Medium/Low)
- Registration status
- Attendance tracking

#### **ANALYTICS (Read-Only)**
| Operation | URL | Description |
|-----------|-----|-------------|
| **READ** | `/placement/` | Dashboard with stats |
| **READ** | `/placement/analytics/` | Detailed analytics |

**Data Displayed:**
- Placement rate calculations
- CGPA distributions
- Branch-wise statistics
- Skill averages
- Prediction distributions

---

## AUTHENTICATION

### College Portal
- **Username:** college
- **Password:** college123
- **Access:** Student management, Marks entry, Subject management

### Placement Portal
- **Username:** placement
- **Password:** placement123
- **Access:** View all data, Manage training sessions, Student recommendations

### Student Portal
- **No Login Required**
- Access with Student ID (e.g., 1XX21CS001)

---

## DATA PERSISTENCE

All operations **immediately save to SQLite database**:

**Auto-Save Features:**
- Student creation/editing
- Subject creation/editing
- Marks entry triggers CGPA recalculation
- Grade auto-calculation on marks save
- Backlog auto-detection
- Training session management
- Recommendation tracking

**Data Integrity:**
- Unique constraints on Student ID and Email
- Foreign key relationships maintained
- Cascade delete for related records
- Transaction safety

---

## SAMPLE OPERATIONS

### Add Student via College Portal:
```
1. Login to College Portal (college/college123)
2. Navigate to "Manage Students"
3. Click "Add Student"
4. Enter:
- Student ID: 1XX21CS006
- Name: Test Student
- Email: test@example.com
- Phone: 1234567890
- Branch: CSE
- Semester: 5
- Batch Year: 2021
5. Click "Add Student"
6. Student saved to database immediately
```

### Enter Marks:
```
1. Go to "Manage Students"
2. Click "Marks" for a student
3. Select Subject
4. Enter Internal Marks (0-50)
5. Enter External Marks (0-100)
6. Submit
7. Marks saved, grade calculated, CGPA updated automatically
```

### Add Subject:
```
1. Go to "Manage Subjects"
2. Click "Add Subject"
3. Enter:
- Subject Code: CS401
- Subject Name: Machine Learning
- Branch: CSE
- Semester: 4
- Credits: 4
4. Submit
5. Subject available for marks entry
```

### Create Training Session:
```
1. Login to Placement Portal (placement/placement123)
2. Navigate to "Training Sessions"
3. Click "Add Session"
4. Fill details (title, type, date, venue, etc.)
5. Submit
6. Session created and visible to all
```

---

## VERIFY DATABASE

Run this command to check database status:
```bash
cd "c:\Placement Predictor"
venv\Scripts\python.exe check_db.py
```

This shows:
- All tables
- Record counts
- Sample data

---

## URLS REFERENCE

### College Portal
- `/college/` - Dashboard
- `/college/students/` - List all students
- `/college/student/add/` - Add student
- `/college/student/<id>/edit/` - Edit student
- `/college/student/<id>/delete/` - Delete student
- `/college/student/<id>/marks/` - Enter marks
- `/college/subjects/` - List all subjects
- `/college/subject/add/` - Add subject
- `/college/subject/<id>/edit/` - Edit subject
- `/college/subject/<id>/delete/` - Delete subject

### Placement Portal
- `/placement/` - Dashboard
- `/placement/sessions/` - List training sessions
- `/placement/session/add/` - Add session
- `/placement/session/<id>/edit/` - Edit session
- `/placement/session/<id>/delete/` - Delete session
- `/placement/student/<id>/` - Student profile
- `/placement/student/<id>/recommend/` - Recommend session
- `/placement/analytics/` - Analytics view

---

## CONFIRMATION

**Everything is now fully functional with SQLite backend!**

- All data persisted in `db.sqlite3`
- Full CRUD operations on Students
- Full CRUD operations on Subjects
- Full CRUD operations on Training Sessions
- VTU-style marks entry with auto-calculations
- Delete confirmations to prevent accidents
- Real-time CGPA and backlog calculations
- All changes immediately reflected in database

**Access your application at:** http://127.0.0.1:8000/
