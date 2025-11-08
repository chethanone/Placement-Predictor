import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'placement_project.settings'
django.setup()

from predictor.models import Subject

# Add subjects for AIML branch (Semester 5)
aiml_subjects_sem5 = [
    {'code': 'AI51', 'name': 'Deep Learning', 'semester': 5, 'credits': 4},
    {'code': 'AI52', 'name': 'Natural Language Processing', 'semester': 5, 'credits': 4},
    {'code': 'AI53', 'name': 'Computer Vision', 'semester': 5, 'credits': 4},
    {'code': 'AI54', 'name': 'Machine Learning', 'semester': 5, 'credits': 4},
    {'code': 'AI55', 'name': 'Big Data Analytics', 'semester': 5, 'credits': 3},
]

# Add subjects for AIML branch (Other semesters)
aiml_all_semesters = [
    # Semester 1
    {'code': 'AI11', 'name': 'Engineering Mathematics-I', 'semester': 1, 'credits': 4},
    {'code': 'AI12', 'name': 'Engineering Physics', 'semester': 1, 'credits': 4},
    {'code': 'AI13', 'name': 'Programming in C', 'semester': 1, 'credits': 3},
    
    # Semester 2
    {'code': 'AI21', 'name': 'Engineering Mathematics-II', 'semester': 2, 'credits': 4},
    {'code': 'AI22', 'name': 'Data Structures', 'semester': 2, 'credits': 4},
    {'code': 'AI23', 'name': 'Python Programming', 'semester': 2, 'credits': 3},
    
    # Semester 3
    {'code': 'AI31', 'name': 'Discrete Mathematics', 'semester': 3, 'credits': 4},
    {'code': 'AI32', 'name': 'Database Management Systems', 'semester': 3, 'credits': 4},
    {'code': 'AI33', 'name': 'Object Oriented Programming', 'semester': 3, 'credits': 3},
    
    # Semester 4
    {'code': 'AI41', 'name': 'Artificial Intelligence', 'semester': 4, 'credits': 4},
    {'code': 'AI42', 'name': 'Operating Systems', 'semester': 4, 'credits': 4},
    {'code': 'AI43', 'name': 'Web Technologies', 'semester': 4, 'credits': 3},
    
    # Semester 5
    {'code': 'AI51', 'name': 'Deep Learning', 'semester': 5, 'credits': 4},
    {'code': 'AI52', 'name': 'Natural Language Processing', 'semester': 5, 'credits': 4},
    {'code': 'AI53', 'name': 'Computer Vision', 'semester': 5, 'credits': 4},
    {'code': 'AI54', 'name': 'Machine Learning', 'semester': 5, 'credits': 4},
    {'code': 'AI55', 'name': 'Big Data Analytics', 'semester': 5, 'credits': 3},
    
    # Semester 6
    {'code': 'AI61', 'name': 'Neural Networks', 'semester': 6, 'credits': 4},
    {'code': 'AI62', 'name': 'Reinforcement Learning', 'semester': 6, 'credits': 4},
    {'code': 'AI63', 'name': 'Cloud Computing', 'semester': 6, 'credits': 3},
]

print("Adding subjects for AIML branch...")
added_count = 0
for subject_data in aiml_all_semesters:
    subject, created = Subject.objects.get_or_create(
        subject_code=subject_data['code'],
        branch='AIML',
        defaults={
            'subject_name': subject_data['name'],
            'semester': subject_data['semester'],
            'credits': subject_data['credits']
        }
    )
    if created:
        print(f"[+] Added: {subject.subject_code} - {subject.subject_name} (Sem {subject.semester})")
        added_count += 1
    else:
        print(f"  Already exists: {subject.subject_code}")

print(f"\nSuccessfully added {added_count} subjects for AIML branch!")

# Verify
from predictor.models import StudentRecord
print("\n=== VERIFICATION ===")
student = StudentRecord.objects.filter(branch='AIML').first()
if student:
    subjects = Subject.objects.filter(branch=student.branch, semester=student.current_semester)
    print(f"Student: {student.name} (Branch: {student.branch}, Semester: {student.current_semester})")
    print(f"Available subjects: {subjects.count()}")
    for subj in subjects:
        print(f"  - {subj.subject_code}: {subj.subject_name}")
