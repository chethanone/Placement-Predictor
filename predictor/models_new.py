

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# ======================
# STUDENT MODELS
# ======================

class StudentRecord(models.Model):
    """Main student record managed by college"""
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science Engineering'),
        ('ISE', 'Information Science Engineering'),
        ('ECE', 'Electronics & Communication'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('EEE', 'Electrical & Electronics'),
    ]
    
    # Student ID (VTU USN format: 1XX21CS001)
    student_id = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    
    # Academic Info
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES)
    current_semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    batch_year = models.IntegerField()  # Year of joining
    
    # Calculated Fields
    cgpa = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    total_backlogs = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.student_id} - {self.name}"
    
    class Meta:
        ordering = ['student_id']


class Subject(models.Model):
    """Subject/Course master"""
    subject_code = models.CharField(max_length=20, unique=True)
    subject_name = models.CharField(max_length=200)
    branch = models.CharField(max_length=10)
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    credits = models.IntegerField(default=3)
    
    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"
    
    class Meta:
        ordering = ['semester', 'subject_code']


class StudentMarks(models.Model):
    """VTU-style marks entry"""
    student = models.ForeignKey(StudentRecord, on_delete=models.CASCADE, related_name='marks')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    
    # VTU Marks Structure
    internal_marks = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        help_text="Internal assessment marks (max 50)"
    )
    external_marks = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="External exam marks (max 100)"
    )
    total_marks = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(150)],
        default=0
    )
    
    # Grading
    grade = models.CharField(max_length=2, blank=True)  # S, A, B, C, D, E, F
    grade_points = models.FloatField(default=0.0)
    is_backlog = models.BooleanField(default=False)
    
    # Metadata
    academic_year = models.CharField(max_length=20)  # e.g., "2024-25"
    entered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    entered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Calculate total marks
        self.total_marks = self.internal_marks + self.external_marks
        
        # Calculate grade and grade points (VTU pattern)
        if self.total_marks >= 135:
            self.grade, self.grade_points = 'S', 10.0
        elif self.total_marks >= 120:
            self.grade, self.grade_points = 'A', 9.0
        elif self.total_marks >= 105:
            self.grade, self.grade_points = 'B', 8.0
        elif self.total_marks >= 90:
            self.grade, self.grade_points = 'C', 7.0
        elif self.total_marks >= 75:
            self.grade, self.grade_points = 'D', 6.0
        elif self.total_marks >= 60:
            self.grade, self.grade_points = 'E', 5.0
        else:
            self.grade, self.grade_points = 'F', 0.0
            self.is_backlog = True
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.student_id} - {self.subject.subject_code} - {self.grade}"
    
    class Meta:
        unique_together = ['student', 'subject', 'semester']
        ordering = ['semester', 'subject']


# ======================
# QUIZ SYSTEM MODELS
# ======================

class StudentQuiz(models.Model):
    """Quiz generated from uploaded PDF/PPT"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    student_id = models.CharField(max_length=20)
    student_name = models.CharField(max_length=200)
    
    # File Upload
    uploaded_file = models.FileField(upload_to='quiz_uploads/')
    file_type = models.CharField(max_length=10)  # pdf, ppt, pptx
    extracted_text = models.TextField(blank=True)
    
    # Quiz Details
    total_questions = models.IntegerField(default=25)
    questions_generated = models.BooleanField(default=False)
    
    # Results
    score = models.FloatField(null=True, blank=True)
    percentage = models.FloatField(null=True, blank=True)
    time_taken = models.IntegerField(null=True, blank=True)  # in seconds
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Recommendations
    recommendations = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Quiz {self.id} - {self.student_name}"
    
    class Meta:
        ordering = ['-created_at']


class QuizQuestion(models.Model):
    """Individual questions for a quiz"""
    QUESTION_TYPES = [
        ('mcq', 'Multiple Choice'),
        ('tf', 'True/False'),
    ]
    
    quiz = models.ForeignKey(StudentQuiz, on_delete=models.CASCADE, related_name='questions')
    question_number = models.IntegerField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='mcq')
    
    question_text = models.TextField()
    option_a = models.CharField(max_length=500, blank=True)
    option_b = models.CharField(max_length=500, blank=True)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)
    
    correct_answer = models.CharField(max_length=1)  # A, B, C, D, T, F
    student_answer = models.CharField(max_length=1, blank=True, null=True)
    is_correct = models.BooleanField(null=True)
    
    explanation = models.TextField(blank=True)
    
    def __str__(self):
        return f"Q{self.question_number} - Quiz {self.quiz.id}"
    
    class Meta:
        ordering = ['question_number']
        unique_together = ['quiz', 'question_number']


# ======================
# PREDICTION MODELS
# ======================

class StudentPrediction(models.Model):
    """Placement prediction for students"""
    student = models.ForeignKey(StudentRecord, on_delete=models.CASCADE, related_name='predictions')
    
    # Input Features (will be fetched from StudentRecord and StudentMarks)
    cgpa = models.FloatField()
    backlogs = models.IntegerField()
    communication_skills = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    technical_skills = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    aptitude_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    projects_completed = models.IntegerField(default=0)
    internships = models.IntegerField(default=0)
    certifications = models.IntegerField(default=0)
    
    # Prediction Results
    placement_probability = models.FloatField()
    prediction = models.CharField(max_length=20)  # Placed/Not Placed
    confidence_score = models.FloatField()
    
    # Recommendations
    recommendations = models.TextField(blank=True)
    
    # Metadata
    predicted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.student_id} - {self.prediction} ({self.placement_probability}%)"
    
    class Meta:
        ordering = ['-predicted_at']


# ======================
# PLACEMENT PORTAL MODELS
# ======================

class TrainingSession(models.Model):
    """Training sessions recommended by placement cell"""
    SESSION_TYPES = [
        ('technical', 'Technical Training'),
        ('aptitude', 'Aptitude Training'),
        ('communication', 'Communication Skills'),
        ('interview', 'Interview Preparation'),
        ('group_discussion', 'Group Discussion'),
        ('resume', 'Resume Building'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    session_type = models.CharField(max_length=30, choices=SESSION_TYPES)
    
    # Schedule
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)
    venue = models.CharField(max_length=200)
    
    # Capacity
    max_students = models.IntegerField(default=50)
    registered_students = models.ManyToManyField(StudentRecord, related_name='training_sessions', blank=True)
    
    # Resources
    resource_links = models.TextField(blank=True, help_text="Comma-separated links")
    
    # Status
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_date}"
    
    class Meta:
        ordering = ['-scheduled_date']


class SessionRecommendation(models.Model):
    """Placement cell recommendations for specific students"""
    student = models.ForeignKey(StudentRecord, on_delete=models.CASCADE, related_name='session_recommendations')
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE)
    
    # Recommendation Details
    reason = models.TextField(help_text="Why this session is recommended")
    priority = models.CharField(max_length=20, choices=[
        ('high', 'High Priority'),
        ('medium', 'Medium Priority'),
        ('low', 'Low Priority'),
    ], default='medium')
    
    # Status
    is_registered = models.BooleanField(default=False)
    is_attended = models.BooleanField(default=False)
    
    # Metadata
    recommended_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    recommended_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.student_id} - {self.session.title}"
    
    class Meta:
        unique_together = ['student', 'session']
        ordering = ['-recommended_at']


# Keep old models for backward compatibility (can be removed later)
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher')
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    firebase_uid = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"
