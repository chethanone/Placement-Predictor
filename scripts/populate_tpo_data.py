"""
Populate sample data for TPO Portal Testing
"""
from predictor.models import (
StudentRecord, Company, EmployabilityScore,
Branch, StudentPrediction
)
from django.contrib.auth.models import User
import random

# Create sample companies
companies_data = [
{'name': 'Google', 'company_type': 'mnc', 'package_min': 15.0, 'package_max': 30.0, 'min_cgpa': 8.0, 'max_backlogs': 0, 'required_branches': 'CSE,ISE', 'total_placements': 45},
{'name': 'Amazon', 'company_type': 'mnc', 'package_min': 18.0, 'package_max': 35.0, 'min_cgpa': 7.5, 'max_backlogs': 0, 'required_branches': 'CSE,ISE,ECE', 'total_placements': 38},
{'name': 'Microsoft', 'company_type': 'mnc', 'package_min': 16.0, 'package_max': 32.0, 'min_cgpa': 8.0, 'max_backlogs': 0, 'required_branches': 'CSE,ISE', 'total_placements': 42},
{'name': 'Infosys', 'company_type': 'service', 'package_min': 3.5, 'package_max': 7.0, 'min_cgpa': 6.5, 'max_backlogs': 2, 'required_branches': '', 'total_placements': 120},
{'name': 'TCS', 'company_type': 'service', 'package_min': 3.2, 'package_max': 6.5, 'min_cgpa': 6.0, 'max_backlogs': 3, 'required_branches': '', 'total_placements': 150},
{'name': 'Wipro', 'company_type': 'service', 'package_min': 3.5, 'package_max': 7.5, 'min_cgpa': 6.5, 'max_backlogs': 2, 'required_branches': '', 'total_placements': 110},
{'name': 'Flipkart', 'company_type': 'product', 'package_min': 12.0, 'package_max': 25.0, 'min_cgpa': 7.5, 'max_backlogs': 0, 'required_branches': 'CSE,ISE', 'total_placements': 35},
{'name': 'Zomato', 'company_type': 'startup', 'package_min': 8.0, 'package_max': 15.0, 'min_cgpa': 7.0, 'max_backlogs': 1, 'required_branches': 'CSE,ISE,ECE', 'total_placements': 25},
{'name': 'Bosch', 'company_type': 'core', 'package_min': 6.5, 'package_max': 12.0, 'min_cgpa': 7.0, 'max_backlogs': 1, 'required_branches': 'ME,ECE,EEE', 'total_placements': 30},
{'name': 'Texas Instruments', 'company_type': 'core', 'package_min': 8.0, 'package_max': 14.0, 'min_cgpa': 7.5, 'max_backlogs': 0, 'required_branches': 'ECE,EEE', 'total_placements': 28},
]

print("Creating companies...")
for comp_data in companies_data:
company, created = Company.objects.get_or_create(
name=comp_data['name'],
defaults=comp_data
)
if created:
print(f" Created: {company.name}")
else:
print(f" Exists: {company.name}")

# Create employability scores for existing students
print("\nCreating employability scores for students...")
students = StudentRecord.objects.filter(is_active=True)

admin_user = User.objects.filter(is_superuser=True).first()

for student in students:
if not hasattr(student, 'employability'):
# Generate realistic scores based on CGPA
base_score = student.cgpa * 5 # Base score from CGPA

communication = min(max(random.gauss(base_score/10, 1.5), 1), 10)
technical = min(max(random.gauss(base_score/10 + 0.5, 1.5), 1), 10)
coding = min(max(random.gauss(base_score/10, 1.5), 1), 10)
aptitude = min(max(random.gauss(base_score * 10, 15), 20), 100)
soft_skills = min(max(random.gauss(base_score/10, 1), 1), 10)

projects = random.randint(0, 5)
internships = random.randint(0, 3)
certifications = random.randint(0, 4)
hackathons = random.randint(0, 3)

emp_score = EmployabilityScore.objects.create(
student=student,
communication_score=round(communication, 1),
technical_score=round(technical, 1),
coding_score=round(coding, 1),
aptitude_score=round(aptitude, 1),
soft_skills_score=round(soft_skills, 1),
projects_count=projects,
internships_count=internships,
certifications_count=certifications,
hackathons_count=hackathons,
assessed_by=admin_user
)
print(f" Created employability for: {student.student_id} - {emp_score.overall_employability:.1f}%")

# Create sample predictions for existing students
print("\nCreating sample predictions...")
for student in students:
if not StudentPrediction.objects.filter(student=student).exists():
try:
emp = EmployabilityScore.objects.get(student=student)

# Calculate placement probability based on employability
placement_prob = min(emp.overall_employability + random.uniform(-10, 10), 100)
placement_prob = max(placement_prob, 0)

prediction = StudentPrediction.objects.create(
student=student,
cgpa=student.cgpa,
backlogs=student.total_backlogs,
communication_skills=emp.communication_score,
technical_skills=emp.technical_score,
aptitude_score=emp.aptitude_score,
projects_completed=emp.projects_count,
internships=emp.internships_count,
certifications=emp.certifications_count,
placement_probability=round(placement_prob, 1),
prediction='Placed' if placement_prob >= 60 else 'Not Placed',
confidence_score=random.uniform(0.75, 0.95),
recommendations=f"Focus on improving {'communication skills' if emp.communication_score < 7 else 'technical skills' if emp.technical_score < 7 else 'coding practice'}."
)
print(f" Created prediction for: {student.student_id} - {prediction.placement_probability}%")
except EmployabilityScore.DoesNotExist:
print(f" Skipped: {student.student_id} (no employability score)")

print("\n" + "="*50)
print("Sample data population complete!")
print("="*50)
print(f"Total Companies: {Company.objects.count()}")
print(f"Total Students: {StudentRecord.objects.count()}")
print(f"Employability Scores: {EmployabilityScore.objects.count()}")
print(f"Predictions: {StudentPrediction.objects.count()}")
print("="*50)
