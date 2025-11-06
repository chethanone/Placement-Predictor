import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'placement_project.settings'
django.setup()

from predictor.models import Subject, StudentRecord, Branch

print('=== CURRENT STATE ===')
print(f'Total Subjects: {Subject.objects.count()}')
print(f'Total Students: {StudentRecord.objects.count()}')
print(f'Total Branches: {Branch.objects.count()}')

print('\n=== SUBJECTS BY BRANCH ===')
for branch in Branch.objects.all():
    subjects = Subject.objects.filter(branch=branch.code)
    print(f'{branch.name} ({branch.code}): {subjects.count()} subjects')

print('\n=== FIRST STUDENT ===')
s = StudentRecord.objects.first()
if s:
    print(f'Name: {s.name}')
    print(f'Branch: {s.branch} ({s.get_branch_display()})')
    print(f'Semester: {s.current_semester}')
    subjects = Subject.objects.filter(branch=s.branch, semester=s.current_semester)
    print(f'Available subjects for marks: {subjects.count()}')
    if subjects.exists():
        print('Subjects:')
        for subj in subjects:
            print(f'  - {subj.subject_code}: {subj.subject_name}')
    else:
        print('NO SUBJECTS FOUND FOR THIS STUDENT!')
        print('\n=== ALL SUBJECTS ===')
        all_subjects = Subject.objects.all()
        for subj in all_subjects:
            print(f'  - {subj.branch}/{subj.semester}: {subj.subject_code} - {subj.subject_name}')
