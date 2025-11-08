"""
New Models for Student-College-Placement System
VTU-Style marks entry and management
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# ======================
# NOTIFICATION MODEL
# ======================

class StudentNotification(models.Model):
    """Notifications for college about student entries"""
    usn = models.CharField(max_length=50)
    college_name = models.CharField(max_length=255)
    requested_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Request for {self.usn} from {self.college_name}"
    
    class Meta:
        ordering = ['-requested_at']

# ======================
# BRANCH MODEL
# ======================

class Branch(models.Model):
    """Dynamic branch management for colleges"""
    code = models.CharField(max_length=10, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        ordering = ['code']
        verbose_name_plural = "Branches"

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
    cgpa_manually_entered = models.BooleanField(default=False, help_text="True if CGPA was entered directly, not calculated")
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
        ('fill_blank', 'Fill in the Blank'),
        ('short_answer', 'Short Answer'),
        ('true_false', 'True/False'),
        ('text', 'Text'),
    ]
    
    quiz = models.ForeignKey(StudentQuiz, on_delete=models.CASCADE, related_name='questions')
    question_number = models.IntegerField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='mcq')
    
    question_text = models.TextField()
    option_a = models.CharField(max_length=500, blank=True)
    option_b = models.CharField(max_length=500, blank=True)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)
    options = models.TextField(blank=True, null=True)  # JSON field for flexible options
    
    correct_answer = models.TextField()  # Changed to TextField to support longer answers
    student_answer = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(null=True)
    
    explanation = models.TextField(blank=True)
    reference_text = models.TextField(blank=True)  # Text snippet from PDF for context
    page_number = models.IntegerField(null=True, blank=True)  # Page number in PDF where answer is found
    
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


# ======================
# TPO PORTAL MODELS
# ======================

class Company(models.Model):
    """Companies for placement"""
    COMPANY_TYPES = [
        ('mnc', 'MNC (Multinational Corporation)'),
        ('startup', 'Startup'),
        ('core', 'Core Company'),
        ('service', 'Service Based'),
        ('product', 'Product Based'),
    ]
    
    name = models.CharField(max_length=200)
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPES)
    
    # Package Details
    package_min = models.FloatField(help_text="Minimum package in LPA")
    package_max = models.FloatField(help_text="Maximum package in LPA")
    
    # Requirements
    min_cgpa = models.FloatField(default=6.0)
    max_backlogs = models.IntegerField(default=0)
    required_branches = models.CharField(max_length=500, help_text="Comma-separated branch codes")
    
    # Skills Required
    technical_skills_min = models.FloatField(default=5.0)
    communication_skills_min = models.FloatField(default=5.0)
    aptitude_score_min = models.FloatField(default=50.0)
    
    # Metadata
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    last_visited = models.DateField(null=True, blank=True)
    total_placements = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_company_type_display()})"
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Companies"


class EmployabilityScore(models.Model):
    """Detailed employability assessment for students"""
    student = models.OneToOneField(StudentRecord, on_delete=models.CASCADE, related_name='employability')
    
    # Skill Scores (0-10)
    communication_score = models.FloatField(default=5.0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    technical_score = models.FloatField(default=5.0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    aptitude_score = models.FloatField(default=50.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    coding_score = models.FloatField(default=5.0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    soft_skills_score = models.FloatField(default=5.0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    
    # Experience
    projects_count = models.IntegerField(default=0)
    internships_count = models.IntegerField(default=0)
    certifications_count = models.IntegerField(default=0)
    hackathons_count = models.IntegerField(default=0)
    
    # Overall Score
    overall_employability = models.FloatField(default=0.0)  # Calculated field (0-100)
    placement_readiness = models.CharField(max_length=20, choices=[
        ('excellent', 'Excellent (90-100%)'),
        ('good', 'Good (70-89%)'),
        ('average', 'Average (50-69%)'),
        ('needs_improvement', 'Needs Improvement (<50%)'),
    ], default='average')
    
    # Recommendations
    skill_gaps = models.TextField(blank=True, help_text="Areas that need improvement")
    recommended_companies = models.ManyToManyField(Company, blank=True, related_name='suitable_students')
    
    # Metadata
    last_assessed = models.DateTimeField(auto_now=True)
    assessed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def calculate_overall_score(self):
        """Calculate overall employability score"""
        # Weighted calculation
        score = (
            self.communication_score * 0.15 * 10 +
            self.technical_score * 0.25 * 10 +
            self.aptitude_score * 0.15 +
            self.coding_score * 0.20 * 10 +
            self.soft_skills_score * 0.10 * 10 +
            (self.student.cgpa / 10) * 0.10 * 100 +
            min(self.projects_count * 2, 5) +
            min(self.internships_count * 3, 5) +
            min(self.certifications_count * 1, 3) +
            min(self.hackathons_count * 2, 3)
        )
        
        self.overall_employability = min(score, 100)
        
        # Determine readiness level
        if self.overall_employability >= 90:
            self.placement_readiness = 'excellent'
        elif self.overall_employability >= 70:
            self.placement_readiness = 'good'
        elif self.overall_employability >= 50:
            self.placement_readiness = 'average'
        else:
            self.placement_readiness = 'needs_improvement'
        
        return self.overall_employability
    
    def save(self, *args, **kwargs):
        self.calculate_overall_score()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.student_id} - {self.overall_employability}%"
    
    class Meta:
        ordering = ['-overall_employability']


class DepartmentAnalytics(models.Model):
    """Department-wise analytics snapshot"""
    branch = models.CharField(max_length=10)
    academic_year = models.CharField(max_length=20)  # e.g., "2024-25"
    
    # Statistics
    total_students = models.IntegerField(default=0)
    avg_cgpa = models.FloatField(default=0.0)
    avg_employability = models.FloatField(default=0.0)
    placement_ready_count = models.IntegerField(default=0)  # Students with >70% employability
    
    # Skill Averages
    avg_communication = models.FloatField(default=0.0)
    avg_technical = models.FloatField(default=0.0)
    avg_coding = models.FloatField(default=0.0)
    avg_aptitude = models.FloatField(default=0.0)
    
    # Trends
    trend = models.CharField(max_length=20, choices=[
        ('improving', 'Improving'),
        ('stable', 'Stable'),
        ('declining', 'Declining'),
    ], default='stable')
    
    # Metadata
    generated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.branch} - {self.academic_year}"
    
    class Meta:
        ordering = ['-generated_at']
        unique_together = ['branch', 'academic_year']


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
