from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class StudentPrediction(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    COLLEGE_TIER_CHOICES = [
        (1, 'Tier 1 (Top colleges)'),
        (2, 'Tier 2 (Good colleges)'),
        (3, 'Tier 3 (Average colleges)'),
    ]
    
    # Personal Information
    name = models.CharField(max_length=200)
    age = models.IntegerField(validators=[MinValueValidator(17), MaxValueValidator(30)])
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    
    # Academic Performance
    cgpa = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    prev_sem_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    
    # Skills & Abilities
    communication_skills = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    iq_score = models.IntegerField(validators=[MinValueValidator(70), MaxValueValidator(150)])
    
    # Projects & Activities
    projects_completed = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(20)])
    extra_curricular_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    
    # Institution
    college_tier = models.IntegerField(choices=COLLEGE_TIER_CHOICES)
    
    # Certifications
    has_certificates = models.BooleanField(default=False)
    certificate_names = models.TextField(blank=True, null=True)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    
    # Prediction Results
    placement_prediction = models.CharField(max_length=10)
    placement_probability = models.FloatField()
    employability_score = models.FloatField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.placement_probability:.2f}%"

class SyllabusAssessment(models.Model):
    student = models.ForeignKey(StudentPrediction, on_delete=models.CASCADE, related_name='assessments')
    syllabus_file = models.FileField(upload_to='syllabi/')
    score = models.FloatField(null=True, blank=True)
    assessment_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-assessment_date']
    
    def __str__(self):
        return f"Assessment for {self.student.name}"

class AssessmentQuestion(models.Model):
    assessment = models.ForeignKey(SyllabusAssessment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    correct_answer = models.TextField()
    student_answer = models.TextField(null=True, blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    
    def __str__(self):
        return f"Q: {self.question_text[:50]}..."

class StudyRecommendation(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low Priority'),
    ]
    
    assessment = models.ForeignKey(SyllabusAssessment, on_delete=models.CASCADE, related_name='recommendations')
    topic = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    resources = models.TextField()  # JSON field storing learning resources
    
    def __str__(self):
        return f"{self.topic} ({self.priority})"


# ==================== NEW MODELS FOR TEACHER-STUDENT SYSTEM ====================

class Teacher(models.Model):
    """Teacher model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    firebase_uid = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"


class Student(models.Model):
    """Student model with Firebase integration"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    roll_number = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    stream = models.CharField(max_length=100)
    year = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    firebase_uid = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.roll_number} - {self.user.get_full_name()}"


class StudentSkillScore(models.Model):
    """Stores skill scores for students (from quizzes and teacher verification)"""
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='skill_scores')
    
    # Academic
    cgpa = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)], default=0)
    previous_semester = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)], default=0)
    backlogs = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    
    # Skills (from quizzes)
    communication_skills = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)], default=0)
    technical_skills = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)], default=0)
    programming_skills = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)], default=0)
    soft_skills = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)], default=0)
    aptitude_score = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(100.0)], default=0)
    
    # Experience
    projects_completed = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    internships = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    certifications = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    extracurricular_activities = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(10.0)], default=0)
    
    # Verification
    verified_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # College
    college_tier = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)], default=2)
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Skills for {self.student.roll_number}"


class SyllabusQuiz(models.Model):
    """Quiz generated from student's syllabus"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('verified', 'Verified by Teacher'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quizzes')
    syllabus_file = models.FileField(upload_to='syllabi/')
    syllabus_text = models.TextField()
    
    # Quiz details
    total_questions = models.IntegerField(default=25)
    score = models.FloatField(null=True, blank=True)
    time_taken = models.IntegerField(null=True, blank=True)  # in seconds
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Quiz for {self.student.roll_number} - {self.status}"


class QuizQuestion(models.Model):
    """Questions generated for a quiz"""
    quiz = models.ForeignKey(SyllabusQuiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    correct_answer = models.TextField()
    student_answer = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(null=True, blank=True)
    marks = models.FloatField(default=1.0)
    
    def __str__(self):
        return f"Q{self.id}: {self.question_text[:50]}..."


class TeacherVerification(models.Model):
    """Teacher verification of student scores"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='verifications')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='verifications')
    quiz = models.ForeignKey(SyllabusQuiz, on_delete=models.CASCADE, null=True, blank=True)
    
    # Original scores (from quiz)
    original_technical = models.FloatField(default=0)
    original_programming = models.FloatField(default=0)
    original_aptitude = models.FloatField(default=0)
    
    # Verified scores (edited by teacher)
    verified_technical = models.FloatField(default=0)
    verified_programming = models.FloatField(default=0)
    verified_aptitude = models.FloatField(default=0)
    
    # Teacher's notes
    notes = models.TextField(blank=True)
    
    # Status
    is_approved = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Verification for {self.student.roll_number} by {self.teacher.user.username}"

