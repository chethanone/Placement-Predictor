import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'placement_project.settings'
django.setup()

from predictor.models import Subject, StudentRecord

print('=== AIML STUDENT CHECK ===')
aiml_student = StudentRecord.objects.filter(branch='AIML').first()
if aiml_student:
    print(f'Student: {aiml_student.name}')
    print(f'ID: {aiml_student.student_id}')
    print(f'Branch: {aiml_student.branch}')
    print(f'Semester: {aiml_student.current_semester}')
    
    subjects = Subject.objects.filter(branch=aiml_student.branch, semester=aiml_student.current_semester)
    print(f'\nAvailable subjects for marks entry: {subjects.count()}')
    if subjects.exists():
        print('\nSubjects:')
        for subj in subjects:
            print(f'  ✓ {subj.subject_code} - {subj.subject_name} ({subj.credits} credits)')
    else:
        print('ERROR: No subjects found!')
else:
    print('No AIML student found')
