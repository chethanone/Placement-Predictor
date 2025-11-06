import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'placement_project.settings'
django.setup()

from predictor.models import Subject, StudentRecord

print('=== ALL STUDENTS ===')
for student in StudentRecord.objects.all():
    print(f'\nStudent: {student.name}')
    print(f'  ID: {student.student_id}')
    print(f'  Branch: {student.branch} ({student.get_branch_display()})')
    print(f'  Semester: {student.current_semester}')
    
    subjects = Subject.objects.filter(branch=student.branch, semester=student.current_semester)
    print(f'  Available subjects: {subjects.count()}')
    if not subjects.exists():
        print('  ⚠️  NO SUBJECTS AVAILABLE!')
