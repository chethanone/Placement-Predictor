from django.contrib import admin
from .models import (
    StudentRecord, Subject, StudentMarks, StudentQuiz, 
    QuizQuestion, StudentPrediction, TrainingSession, 
    SessionRecommendation, Teacher
)

@admin.register(StudentRecord)
class StudentRecordAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'name', 'email', 'branch', 'current_semester', 'cgpa', 'total_backlogs']
    list_filter = ['branch', 'current_semester', 'batch_year']
    search_fields = ['student_id', 'name', 'email']
    ordering = ['student_id']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['subject_code', 'subject_name', 'branch', 'semester', 'credits']
    list_filter = ['branch', 'semester']
    search_fields = ['subject_code', 'subject_name']
    ordering = ['semester', 'subject_code']

@admin.register(StudentMarks)
class StudentMarksAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'semester', 'internal_marks', 'external_marks', 'total_marks', 'grade', 'is_backlog']
    list_filter = ['semester', 'grade', 'is_backlog']
    search_fields = ['student__student_id', 'student__name', 'subject__subject_code']
    ordering = ['-semester']

@admin.register(StudentQuiz)
class StudentQuizAdmin(admin.ModelAdmin):
    list_display = ['id', 'student_name', 'file_type', 'total_questions', 'score', 'percentage', 'status', 'created_at']
    list_filter = ['status', 'file_type']
    search_fields = ['student_id', 'student_name']
    ordering = ['-created_at']

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'question_number', 'question_type', 'is_correct']
    list_filter = ['question_type', 'is_correct']
    search_fields = ['question_text']
    ordering = ['quiz', 'question_number']

@admin.register(StudentPrediction)
class StudentPredictionAdmin(admin.ModelAdmin):
    list_display = ['student', 'prediction', 'placement_probability', 'confidence_score', 'predicted_at']
    list_filter = ['prediction']
    search_fields = ['student__student_id', 'student__name']
    ordering = ['-predicted_at']

@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'session_type', 'scheduled_date', 'scheduled_time', 'venue', 'max_students', 'is_active']
    list_filter = ['session_type', 'is_active', 'scheduled_date']
    search_fields = ['title', 'description']
    ordering = ['-scheduled_date']
    filter_horizontal = ['registered_students']

@admin.register(SessionRecommendation)
class SessionRecommendationAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'priority', 'is_registered', 'is_attended', 'recommended_at']
    list_filter = ['priority', 'is_registered', 'is_attended']
    search_fields = ['student__student_id', 'student__name', 'session__title']
    ordering = ['-recommended_at']

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'department', 'phone']
    search_fields = ['employee_id', 'user__username', 'department']
    ordering = ['employee_id']
