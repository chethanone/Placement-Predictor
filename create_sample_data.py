"""
Script to create sample data for testing the 3-portal system
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'placement_project.settings')
django.setup()

from django.contrib.auth.models import User
from predictor.models import StudentRecord, Subject, StudentMarks, TrainingSession

# Create users
print("Creating users...")
try:
    college_user = User.objects.get(username='college')
    college_user.set_password('college123')
    college_user.save()
except:
    college_user = User.objects.create_user('college', 'college@example.com', 'college123')

try:
    placement_user = User.objects.get(username='placement')
    placement_user.set_password('placement123')
    placement_user.save()
except:
    placement_user = User.objects.create_user('placement', 'placement@example.com', 'placement123')

print(" Users created: college/college123, placement/placement123")

# Create sample students
print("\nCreating sample students...")
students_data = [
    {'id': '1XX21CS001', 'name': 'Raj Kumar', 'email': 'raj@student.com', 'phone': '9876543210', 'branch': 'CSE', 'sem': 6, 'cgpa': 8.5, 'batch': 2021},
    {'id': '1XX21CS002', 'name': 'Priya Sharma', 'email': 'priya@student.com', 'phone': '9876543211', 'branch': 'CSE', 'sem': 6, 'cgpa': 9.2, 'batch': 2021},
    {'id': '1XX21ISE001', 'name': 'Amit Patel', 'email': 'amit@student.com', 'phone': '9876543212', 'branch': 'ISE', 'sem': 6, 'cgpa': 7.8, 'batch': 2021},
    {'id': '1XX21ECE001', 'name': 'Sneha Reddy', 'email': 'sneha@student.com', 'phone': '9876543213', 'branch': 'ECE', 'sem': 6, 'cgpa': 8.9, 'batch': 2021},
    {'id': '1XX21ME001', 'name': 'Vikram Singh', 'email': 'vikram@student.com', 'phone': '9876543214', 'branch': 'ME', 'sem': 6, 'cgpa': 7.5, 'batch': 2021},
]

for std in students_data:
    StudentRecord.objects.get_or_create(
        student_id=std['id'],
        defaults={
            'name': std['name'],
            'email': std['email'],
            'phone': std['phone'],
            'branch': std['branch'],
            'current_semester': std['sem'],
            'cgpa': std['cgpa'],
            'batch_year': std['batch']
        }
    )

print(f" Created {len(students_data)} sample students")

# Create sample subjects
print("\nCreating sample subjects...")
subjects_data = [
    {'code': '18CS61', 'name': 'Machine Learning', 'branch': 'CSE', 'sem': 6, 'credits': 4},
    {'code': '18CS62', 'name': 'Computer Networks', 'branch': 'CSE', 'sem': 6, 'credits': 4},
    {'code': '18CS63', 'name': 'Web Technology', 'branch': 'CSE', 'sem': 6, 'credits': 3},
    {'code': '18IS61', 'name': 'Cloud Computing', 'branch': 'ISE', 'sem': 6, 'credits': 4},
    {'code': '18EC61', 'name': 'Digital Communication', 'branch': 'ECE', 'sem': 6, 'credits': 4},
    {'code': '18ME61', 'name': 'CAD/CAM', 'branch': 'ME', 'sem': 6, 'credits': 4},
]

for subj in subjects_data:
    Subject.objects.get_or_create(
        subject_code=subj['code'],
        defaults={
            'subject_name': subj['name'],
            'branch': subj['branch'],
            'semester': subj['sem'],
            'credits': subj['credits']
        }
    )

print(f" Created {len(subjects_data)} sample subjects")

# Create sample training sessions
print("\nCreating training sessions...")
from datetime import datetime, timedelta, time

sessions_data = [
    {'title': 'Python Programming Workshop', 'type': 'technical', 'desc': 'Learn Python from basics to advanced'},
    {'title': 'Aptitude Test Preparation', 'type': 'aptitude', 'desc': 'Quantitative and logical reasoning'},
    {'title': 'Communication Skills', 'type': 'communication', 'desc': 'Improve verbal and written communication'},
    {'title': 'Mock Interview Session', 'type': 'interview', 'desc': 'Practice technical and HR interviews'},
    {'title': 'Group Discussion Training', 'type': 'gd', 'desc': 'Learn effective group discussion skills'},
    {'title': 'Resume Building Workshop', 'type': 'resume', 'desc': 'Create professional resumes'},
]

base_date = datetime.now() + timedelta(days=7)
for i, sess in enumerate(sessions_data):
    TrainingSession.objects.get_or_create(
        title=sess['title'],
        defaults={
            'description': sess['desc'],
            'session_type': sess['type'],
            'scheduled_date': base_date.date() + timedelta(days=i*2),
            'scheduled_time': time(14, 0),  # 2 PM
            'max_students': 30,
            'is_active': True
        }
    )

print(f" Created {len(sessions_data)} training sessions")

print("\n" + "="*60)
print("SAMPLE DATA CREATED SUCCESSFULLY!")
print("="*60)
print("\n 3-PORTAL SYSTEM READY:")
print("\n1. STUDENT PORTAL (No Login):")
print(" - Go to: http://localhost:8000/")
print(" - Click 'Student Portal'")
print(" - Use Student ID: 1XX21CS001")
print("\n2. COLLEGE PORTAL (Login Required):")
print(" - Go to: http://localhost:8000/college/login/")
print(" - Username: college")
print(" - Password: college123")
print("\n3. PLACEMENT PORTAL (Login Required):")
print(" - Go to: http://localhost:8000/placement/login/")
print(" - Username: placement")
print(" - Password: placement123")
print("\n" + "="*60)
