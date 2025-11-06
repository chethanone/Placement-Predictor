import os
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'placement_project.settings'
django.setup()

from predictor.models import Subject

# Comprehensive subject database for all branches and semesters
all_subjects = {
    'CSE': {
        5: [
            {'code': '18CS51', 'name': 'Management & Entrepreneurship', 'credits': 3},
            {'code': '18CS52', 'name': 'Computer Networks', 'credits': 4},
            {'code': '18CS53', 'name': 'Database Management System', 'credits': 4},
            {'code': '18CS54', 'name': 'Automata Theory', 'credits': 3},
            {'code': '18CS55', 'name': 'Application Development using Python', 'credits': 3},
        ],
        6: [
            {'code': '18CS61', 'name': 'Machine Learning', 'credits': 4},
            {'code': '18CS62', 'name': 'Computer Networks', 'credits': 4},
            {'code': '18CS63', 'name': 'Web Technology', 'credits': 3},
        ],
        7: [
            {'code': '18CS71', 'name': 'Artificial Intelligence', 'credits': 4},
            {'code': '18CS72', 'name': 'Cloud Computing', 'credits': 3},
            {'code': '18CS73', 'name': 'Big Data Analytics', 'credits': 4},
        ],
    },
    'ECE': {
        5: [
            {'code': '18EC51', 'name': 'Digital Signal Processing', 'credits': 4},
            {'code': '18EC52', 'name': 'Microcontroller', 'credits': 4},
            {'code': '18EC53', 'name': 'Communication Theory', 'credits': 3},
        ],
        6: [
            {'code': '18EC61', 'name': 'VLSI Design', 'credits': 4},
        ],
    },
    'ISE': {
        5: [
            {'code': '18IS51', 'name': 'Software Engineering', 'credits': 4},
            {'code': '18IS52', 'name': 'Operating Systems', 'credits': 4},
            {'code': '18IS53', 'name': 'Database Management', 'credits': 3},
        ],
        6: [
            {'code': '18IS61', 'name': 'Web Programming', 'credits': 4},
        ],
    },
    'ME': {
        5: [
            {'code': '18ME51', 'name': 'Fluid Mechanics', 'credits': 4},
            {'code': '18ME52', 'name': 'Heat Transfer', 'credits': 4},
            {'code': '18ME53', 'name': 'Machine Design', 'credits': 3},
        ],
        6: [
            {'code': '18ME61', 'name': 'Automobile Engineering', 'credits': 4},
        ],
    },
    'CE': {
        5: [
            {'code': '18CE51', 'name': 'Structural Analysis', 'credits': 4},
            {'code': '18CE52', 'name': 'Geotechnical Engineering', 'credits': 4},
            {'code': '18CE53', 'name': 'Water Resources Engineering', 'credits': 3},
        ],
        6: [
            {'code': '18CE61', 'name': 'Design of Concrete Structures', 'credits': 4},
            {'code': '18CE62', 'name': 'Transportation Engineering', 'credits': 3},
        ],
    },
    'EEE': {
        5: [
            {'code': '18EE51', 'name': 'Power Systems', 'credits': 4},
            {'code': '18EE52', 'name': 'Control Systems', 'credits': 4},
            {'code': '18EE53', 'name': 'Electrical Machines', 'credits': 3},
        ],
        6: [
            {'code': '18EE61', 'name': 'Power Electronics', 'credits': 4},
            {'code': '18EE62', 'name': 'Electric Drives', 'credits': 3},
        ],
    },
}

print("=" * 60)
print("POPULATING COMPREHENSIVE SUBJECT DATABASE")
print("=" * 60)

total_added = 0
for branch_code, semesters in all_subjects.items():
    print(f"\n📚 Adding subjects for {branch_code} branch...")
    for semester, subjects in semesters.items():
        for subject_data in subjects:
            subject, created = Subject.objects.get_or_create(
                subject_code=subject_data['code'],
                branch=branch_code,
                defaults={
                    'subject_name': subject_data['name'],
                    'semester': semester,
                    'credits': subject_data['credits']
                }
            )
            if created:
                print(f"  ✓ Sem {semester}: {subject.subject_code} - {subject.subject_name}")
                total_added += 1

print(f"\n{'=' * 60}")
print(f"Successfully added {total_added} new subjects!")
print(f"Total subjects in database: {Subject.objects.count()}")
print(f"{'=' * 60}")

# Verify all students now have subjects
print("\n" + "=" * 60)
print("VERIFICATION: CHECKING ALL STUDENTS")
print("=" * 60)

from predictor.models import StudentRecord

all_ok = True
for student in StudentRecord.objects.all():
    subjects = Subject.objects.filter(branch=student.branch, semester=student.current_semester)
    status = "[OK]" if subjects.exists() else "[MISSING]"
    print(f"{status} {student.name} ({student.branch} Sem {student.current_semester}): {subjects.count()} subjects")
    if not subjects.exists():
        all_ok = False

print("=" * 60)
if all_ok:
    print("SUCCESS: All students now have subjects available!")
else:
    print("WARNING: Some students still missing subjects - may need manual addition")
print("=" * 60)
