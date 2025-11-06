import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

print("\n=== DATABASE TABLES ===")
predictor_tables = [t for t in tables if 'predictor' in t.lower()]
for table in predictor_tables:
print(f" {table}")

# Check StudentRecord table
print("\n=== STUDENT RECORDS ===")
try:
cursor.execute("SELECT COUNT(*) FROM predictor_studentrecord")
count = cursor.fetchone()[0]
print(f"Total Students: {count}")

if count > 0:
cursor.execute("SELECT student_id, name, branch, phone FROM predictor_studentrecord LIMIT 5")
print("\nSample Students:")
for row in cursor.fetchall():
print(f" • {row[0]} - {row[1]} ({row[2]}) - Phone: {row[3]}")
except Exception as e:
print(f"Error: {e}")

# Check other tables
print("\n=== OTHER TABLES ===")
try:
cursor.execute("SELECT COUNT(*) FROM predictor_subject")
print(f"Subjects: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM predictor_studentmarks")
print(f"Student Marks: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM predictor_studentquiz")
print(f"Quizzes: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM predictor_studentprediction")
print(f"Predictions: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM predictor_trainingsession")
print(f"Training Sessions: {cursor.fetchone()[0]}")
except Exception as e:
print(f"Error: {e}")

conn.close()
print("\n Database check complete!\n")
