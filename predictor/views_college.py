"""
College Portal Views (Login Required)
VTU-style marks entry and CGPA calculation
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from .models import StudentRecord, Subject, StudentMarks, StudentNotification, Branch
from django.db.models import Avg, Count, Q, Sum
import csv
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime

def college_login(request):
    """College portal login"""
    # Clear any existing messages when displaying login page
    if request.method == 'GET':
        storage = messages.get_messages(request)
        storage.used = True
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('college_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'predictor/college/login.html')

@login_required
def college_dashboard(request):
    """College dashboard with statistics"""
    total_students = StudentRecord.objects.count()
    avg_cgpa = StudentRecord.objects.aggregate(Avg('cgpa'))['cgpa__avg'] or 0
    students_with_backlogs = StudentRecord.objects.filter(total_backlogs__gt=0).count()
    
    # Branch-wise statistics
    branch_stats = StudentRecord.objects.values('branch').annotate(
        count=Count('student_id'),
        avg_cgpa=Avg('cgpa')
    )
    
    # Recent students (last 10)
    recent_students = StudentRecord.objects.all().order_by('-created_at')[:10]
    
    context = {
        'total_students': total_students,
        'avg_cgpa': round(avg_cgpa, 2),
        'students_with_backlogs': students_with_backlogs,
        'branch_stats': branch_stats,
        'recent_students': recent_students
    }
    
    return render(request, 'predictor/college/dashboard_modern.html', context)

@login_required
def manage_students(request):
    """List all students"""
    students = StudentRecord.objects.all().order_by('student_id')
    
    # Filter by branch if specified
    branch = request.GET.get('branch')
    if branch:
        students = students.filter(branch=branch)
    
    # Filter by semester
    semester = request.GET.get('semester')
    if semester:
        students = students.filter(current_semester=semester)
    
    # Get branches from Branch model
    branches = Branch.objects.filter(is_active=True).order_by('code')
    
    context = {
        'students': students,
        'branches': branches,
        'semesters': range(1, 9)
    }
    
    return render(request, 'predictor/college/manage_students_modern.html', context)

@login_required
def add_student(request):
    """Add new student"""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        branch = request.POST.get('branch')
        current_semester = request.POST.get('current_semester')
        batch_year = request.POST.get('batch_year', 2024)  # Default to current year
        cgpa = request.POST.get('cgpa', '')  # Optional CGPA
        
        try:
            student = StudentRecord.objects.create(
                student_id=student_id,
                name=name,
                email=email,
                phone=phone,
                branch=branch,
                current_semester=current_semester,
                batch_year=batch_year
            )
            
            # If CGPA is provided, set it as manually entered
            if cgpa and float(cgpa) > 0:
                student.cgpa = float(cgpa)
                student.cgpa_manually_entered = True
                student.save()
            
            messages.success(request, f'Student {student_id} added successfully!')
            return redirect('college_manage_students')
        except Exception as e:
            messages.error(request, f'Error adding student: {str(e)}')
    
    # Get branches from Branch model
    branches = Branch.objects.filter(is_active=True).order_by('code')
    
    context = {
        'branches': branches,
        'semesters': range(1, 9),
        'current_year': 2025
    }
    
    return render(request, 'predictor/college/add_student_modern.html', context)

@login_required
def edit_student(request, student_id):
    """Edit student details"""
    student = get_object_or_404(StudentRecord, student_id=student_id)
    
    if request.method == 'POST':
        student.name = request.POST.get('name')
        student.email = request.POST.get('email')
        student.phone = request.POST.get('phone')
        student.branch = request.POST.get('branch')
        student.current_semester = request.POST.get('current_semester')
        student.batch_year = request.POST.get('batch_year', student.batch_year)
        
        # Handle CGPA update
        cgpa = request.POST.get('cgpa', '')
        if cgpa:
            student.cgpa = float(cgpa)
            student.cgpa_manually_entered = True
        
        try:
            student.save()
            messages.success(request, f'Student {student_id} updated successfully!')
            return redirect('college_manage_students')
        except Exception as e:
            messages.error(request, f'Error updating student: {str(e)}')
    
    # Get branches from Branch model
    branches = Branch.objects.filter(is_active=True).order_by('code')
    
    context = {
        'student': student,
        'branches': branches,
        'semesters': range(1, 9)
    }
    
    return render(request, 'predictor/college/edit_student_modern.html', context)

@login_required
def enter_student_marks(request, student_id):
    """VTU-style marks entry"""
    student = get_object_or_404(StudentRecord, student_id=student_id)
    
    if request.method == 'POST':
        subject_id = request.POST.get('subject')
        internal_marks = int(request.POST.get('internal_marks'))
        external_marks = int(request.POST.get('external_marks'))
        
        subject = Subject.objects.get(id=subject_id)
        
        # Get current academic year (e.g., "2024-25")
        from datetime import datetime
        current_year = datetime.now().year
        academic_year = f"{current_year}-{str(current_year + 1)[-2:]}"
        
        # Create or update marks
        marks, created = StudentMarks.objects.update_or_create(
            student=student,
            subject=subject,
            semester=student.current_semester,
            defaults={
                'internal_marks': internal_marks,
                'external_marks': external_marks,
                'academic_year': academic_year,
                'entered_by': request.user if request.user.is_authenticated else None
            }
        )
        
        # Recalculate CGPA
        recalculate_cgpa(student)
        
        messages.success(request, f'Marks entered successfully for {subject.subject_name}!')
        return redirect('college_enter_marks', student_id=student_id)
    
    # Get subjects for student's branch and semester
    subjects = Subject.objects.filter(
        branch=student.branch,
        semester=student.current_semester
    )
    
    # Get existing marks
    existing_marks = StudentMarks.objects.filter(student=student)
    
    context = {
        'student': student,
        'subjects': subjects,
        'existing_marks': existing_marks
    }
    
    return render(request, 'predictor/college/enter_marks.html', context)

def recalculate_cgpa(student):
    """Recalculate student's CGPA based on all marks (only if not manually entered)"""
    # Don't recalculate if CGPA was manually entered
    if student.cgpa_manually_entered:
        return
    
    marks = StudentMarks.objects.filter(student=student)
    
    total_credits = 0
    weighted_sum = 0
    backlogs = 0
    
    for mark in marks:
        # Refresh from database to ensure grade_points are calculated
        mark.refresh_from_db()
        
        subject_credits = mark.subject.credits
        total_credits += subject_credits
        weighted_sum += mark.grade_points * subject_credits
        
        if mark.is_backlog:
            backlogs += 1
    
    if total_credits > 0:
        student.cgpa = round(weighted_sum / total_credits, 2)
        student.total_backlogs = backlogs
        student.save()

@login_required
def switch_cgpa_mode(request, student_id):
    """Switch between manual CGPA entry and calculated CGPA"""
    student = get_object_or_404(StudentRecord, student_id=student_id)
    
    if request.method == 'POST':
        mode = request.POST.get('mode')
        
        if mode == 'calculated':
            # Switch to calculated mode
            student.cgpa_manually_entered = False
            student.save()
            # Recalculate CGPA from marks
            recalculate_cgpa(student)
            messages.success(request, 'Switched to calculated CGPA mode. CGPA will be calculated from marks.')
        else:
            # Switch to manual mode
            manual_cgpa = request.POST.get('manual_cgpa')
            if manual_cgpa:
                student.cgpa = float(manual_cgpa)
                student.cgpa_manually_entered = True
                student.save()
                messages.success(request, f'CGPA manually set to {student.cgpa}. Automatic calculation disabled.')
        
        return redirect('college_enter_marks', student_id=student_id)
    
    return redirect('college_enter_marks', student_id=student_id)

@login_required
def delete_student(request, student_id):
    """Delete student (soft delete by marking inactive)"""
    student = get_object_or_404(StudentRecord, student_id=student_id)
    
    if request.method == 'POST':
        # Hard delete option
        student.delete()
        messages.success(request, f'Student {student_id} deleted successfully!')
        return redirect('college_manage_students')
    
    context = {'student': student}
    return render(request, 'predictor/college/delete_student_confirm.html', context)

# ==================== SUBJECT MANAGEMENT ====================

@login_required
def manage_subjects(request):
    """List all subjects"""
    subjects = Subject.objects.all().order_by('semester', 'subject_code')
    
    # Filter by branch
    branch = request.GET.get('branch')
    if branch:
        subjects = subjects.filter(branch=branch)
    
    # Filter by semester
    semester = request.GET.get('semester')
    if semester:
        subjects = subjects.filter(semester=semester)
    
    context = {
        'subjects': subjects,
        'branches': StudentRecord.BRANCH_CHOICES,
        'semesters': range(1, 9)
    }
    
    return render(request, 'predictor/college/manage_subjects_modern.html', context)

@login_required
def add_subject(request):
    """Add new subject"""
    if request.method == 'POST':
        subject_code = request.POST.get('subject_code')
        subject_name = request.POST.get('subject_name')
        branch = request.POST.get('branch')
        semester = request.POST.get('semester')
        credits = request.POST.get('credits', 3)
        
        try:
            Subject.objects.create(
                subject_code=subject_code,
                subject_name=subject_name,
                branch=branch,
                semester=semester,
                credits=credits
            )
            messages.success(request, f'Subject {subject_code} added successfully!')
            return redirect('manage_subjects')
        except Exception as e:
            messages.error(request, f'Error adding subject: {str(e)}')
    
    context = {
        'branches': StudentRecord.BRANCH_CHOICES,
        'semesters': range(1, 9)
    }
    
    return render(request, 'predictor/college/add_subject_modern.html', context)

@login_required
def edit_subject(request, subject_id):
    """Edit subject details"""
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        subject.subject_code = request.POST.get('subject_code')
        subject.subject_name = request.POST.get('subject_name')
        subject.branch = request.POST.get('branch')
        subject.semester = request.POST.get('semester')
        subject.credits = request.POST.get('credits')
        
        try:
            subject.save()
            messages.success(request, f'Subject {subject.subject_code} updated successfully!')
            return redirect('manage_subjects')
        except Exception as e:
            messages.error(request, f'Error updating subject: {str(e)}')
    
    context = {
        'subject': subject,
        'branches': StudentRecord.BRANCH_CHOICES,
        'semesters': range(1, 9)
    }
    
    return render(request, 'predictor/college/edit_subject_modern.html', context)

@login_required
def delete_subject(request, subject_id):
    """Delete subject"""
    subject = get_object_or_404(Subject, id=subject_id)
    
    if request.method == 'POST':
        subject_code = subject.subject_code
        subject.delete()
        messages.success(request, f'Subject {subject_code} deleted successfully!')
        return redirect('manage_subjects')
    
    context = {'subject': subject}
    return render(request, 'predictor/college/delete_subject_confirm.html', context)

@login_required
def college_logout(request):
    """Logout"""
    # Clear all messages before logout
    storage = messages.get_messages(request)
    storage.used = True
    
    logout(request)
    return redirect('college_login')

@login_required
def college_notifications(request):
    """View notifications about denied student access attempts"""
    notifications = StudentNotification.objects.filter(is_resolved=False).order_by('-requested_at')
    
    # Mark as resolved if requested
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        if notification_id:
            notification = get_object_or_404(StudentNotification, id=notification_id)
            notification.is_resolved = True
            notification.resolved_at = timezone.now()
            notification.save()
            messages.success(request, 'Notification marked as resolved')
            return redirect('college_notifications')
    
    context = {
        'notifications': notifications,
        'unresolved_count': notifications.count()
    }
    
    return render(request, 'predictor/college/notifications.html', context)

@login_required
def college_analytics(request):
    """Analytics dashboard with comprehensive insights"""
    students = StudentRecord.objects.all()
    
    # Overall stats
    total_students = students.count()
    avg_cgpa = students.aggregate(Avg('cgpa'))['cgpa__avg'] or 0
    students_with_backlogs = students.filter(total_backlogs__gt=0).count()
    
    # Pass percentage (students with CGPA >= 6.0)
    passing_students = students.filter(cgpa__gte=6.0).count()
    pass_percentage = (passing_students / total_students * 100) if total_students > 0 else 0
    
    # Department-wise statistics
    department_stats = []
    for branch_code, branch_name in StudentRecord.BRANCH_CHOICES:
        branch_students = students.filter(branch=branch_code)
        branch_count = branch_students.count()
        
        if branch_count > 0:
            branch_avg_cgpa = branch_students.aggregate(Avg('cgpa'))['cgpa__avg'] or 0
            branch_passing = branch_students.filter(cgpa__gte=6.0).count()
            branch_pass_rate = (branch_passing / branch_count * 100)
            
            # Placement rate estimation (students with CGPA >= 7.0)
            placement_ready = branch_students.filter(cgpa__gte=7.0).count()
            placement_rate = (placement_ready / branch_count * 100)
            
            # Performance score (weighted average)
            performance = (branch_avg_cgpa / 10 * 50) + (branch_pass_rate / 100 * 30) + (placement_rate / 100 * 20)
            
            department_stats.append({
                'branch': branch_name,
                'branch_code': branch_code,
                'count': branch_count,
                'avg_cgpa': branch_avg_cgpa,
                'pass_rate': branch_pass_rate,
                'placement_rate': placement_rate,
                'performance': performance
            })
    
    # Sort by performance score
    department_stats.sort(key=lambda x: x['performance'], reverse=True)
    
    context = {
        'total_students': total_students,
        'avg_cgpa': avg_cgpa,
        'students_with_backlogs': students_with_backlogs,
        'pass_percentage': pass_percentage,
        'department_stats': department_stats
    }
    
    return render(request, 'predictor/college/analytics.html', context)

@login_required
def college_reports(request):
    """Reports page for downloading/exporting data"""
    students = StudentRecord.objects.all()
    
    # Report generation statistics
    total_students = students.count()
    departments = StudentRecord.BRANCH_CHOICES
    semesters = range(1, 9)
    
    context = {
        'total_students': total_students,
        'departments': departments,
        'semesters': semesters
    }
    
    return render(request, 'predictor/college/reports.html', context)

@login_required
def download_report(request, report_type, format):
    """Download pre-defined reports in PDF or CSV format"""
    
    if report_type == 'students':
        # All students report
        students = StudentRecord.objects.all().order_by('student_id')
        
        if format == 'csv':
            return generate_students_csv(students, 'all_students_report')
        elif format == 'pdf':
            return generate_students_pdf(students, 'All Students Report')
    
    elif report_type == 'performance':
        # Performance report with CGPA and academics
        students = StudentRecord.objects.all().order_by('-cgpa')
        
        if format == 'csv':
            return generate_performance_csv(students)
        elif format == 'pdf':
            return generate_performance_pdf(students)
    
    elif report_type == 'backlogs':
        # Students with backlogs
        students = StudentRecord.objects.filter(total_backlogs__gt=0).order_by('-total_backlogs')
        
        if format == 'csv':
            return generate_backlogs_csv(students)
        elif format == 'pdf':
            return generate_backlogs_pdf(students)
    
    elif report_type == 'placement':
        # Placement ready students (CGPA >= 6.5, no backlogs)
        students = StudentRecord.objects.filter(cgpa__gte=6.5, total_backlogs=0).order_by('-cgpa')
        
        if format == 'csv':
            return generate_students_csv(students, 'placement_ready_report')
        elif format == 'pdf':
            return generate_students_pdf(students, 'Placement Ready Students')
    
    messages.error(request, 'Invalid report type or format')
    return redirect('college_reports')

@login_required
def generate_custom_report(request):
    """Generate custom report based on filters"""
    if request.method == 'POST':
        # Get filters from POST data
        branch = request.POST.get('department')
        semester = request.POST.get('semester')
        cgpa_min = request.POST.get('cgpa_min')
        cgpa_max = request.POST.get('cgpa_max')
        format_type = request.POST.get('format', 'csv')
        
        # Get selected fields
        selected_fields = request.POST.getlist('field')
        if not selected_fields:
            selected_fields = ['usn', 'name', 'branch', 'cgpa']  # Default fields
        
        # Build query
        students = StudentRecord.objects.all()
        
        if branch:
            students = students.filter(branch=branch)
        if semester:
            students = students.filter(current_semester=int(semester))
        if cgpa_min:
            students = students.filter(cgpa__gte=float(cgpa_min))
        if cgpa_max:
            students = students.filter(cgpa__lte=float(cgpa_max))
        
        students = students.order_by('student_id')
        
        # Generate report
        if format_type == 'csv':
            return generate_students_csv_custom(students, 'custom_report', selected_fields)
        else:
            return generate_students_pdf_custom(students, 'Custom Student Report', selected_fields)
    
    return redirect('college_reports')

# Helper functions for CSV generation
def generate_students_csv_custom(students, filename, selected_fields):
    """Generate CSV for students with selected fields"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    # Define field mapping
    field_mapping = {
        'usn': ('Student ID', lambda s: s.student_id),
        'name': ('Name', lambda s: s.name),
        'branch': ('Branch', lambda s: s.get_branch_display()),
        'cgpa': ('CGPA', lambda s: f"{s.cgpa:.2f}"),
        'phone': ('Phone', lambda s: s.phone or 'N/A'),
        'email': ('Email', lambda s: s.email or 'N/A'),
        'backlogs': ('Backlogs', lambda s: s.total_backlogs),
        'batch': ('Batch', lambda s: s.batch_year)
    }
    
    # Write header row
    headers = [field_mapping[field][0] for field in selected_fields if field in field_mapping]
    writer.writerow(headers)
    
    # Write data rows
    for student in students:
        row = [field_mapping[field][1](student) for field in selected_fields if field in field_mapping]
        writer.writerow(row)
    
    return response

def generate_students_pdf_custom(students, title, selected_fields):
    """Generate PDF for students with selected fields"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#8FB9A8'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Title
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Define field mapping
    field_mapping = {
        'usn': ('ID', lambda s: s.student_id, 1.2),
        'name': ('Name', lambda s: s.name[:20], 2),
        'branch': ('Branch', lambda s: s.branch, 0.8),
        'cgpa': ('CGPA', lambda s: f"{s.cgpa:.2f}", 0.7),
        'phone': ('Phone', lambda s: s.phone or 'N/A', 1.2),
        'email': ('Email', lambda s: (s.email[:20] + '...') if s.email and len(s.email) > 20 else (s.email or 'N/A'), 1.8),
        'backlogs': ('Backlogs', lambda s: str(s.total_backlogs), 0.8),
        'batch': ('Batch', lambda s: str(s.batch_year), 0.7)
    }
    
    # Table data - header
    headers = [field_mapping[field][0] for field in selected_fields if field in field_mapping]
    data = [headers]
    
    # Table data - rows
    for student in students:
        row = [str(field_mapping[field][1](student)) for field in selected_fields if field in field_mapping]
        data.append(row)
    
    # Calculate column widths
    col_widths = [field_mapping[field][2] * inch for field in selected_fields if field in field_mapping]
    
    # Create table
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8FB9A8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9f5')])
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="custom_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    return response

def generate_students_csv(students, filename):
    """Generate CSV for students"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Name', 'Branch', 'Semester', 'CGPA', 'Backlogs', 'Email', 'Phone', 'Batch'])
    
    for student in students:
        writer.writerow([
            student.student_id,
            student.name,
            student.get_branch_display(),
            student.current_semester,
            f"{student.cgpa:.2f}",
            student.total_backlogs,
            student.email,
            student.phone,
            student.batch_year
        ])
    
    return response

def generate_performance_csv(students):
    """Generate performance CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="performance_report_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Name', 'Branch', 'Semester', 'CGPA', 'Backlogs', 'Status'])
    
    for student in students:
        if student.cgpa >= 8.0:
            status = 'Excellent'
        elif student.cgpa >= 6.5:
            status = 'Good'
        elif student.cgpa >= 5.0:
            status = 'Average'
        else:
            status = 'Need Attention'
        
        writer.writerow([
            student.student_id,
            student.name,
            student.get_branch_display(),
            student.current_semester,
            f"{student.cgpa:.2f}",
            student.total_backlogs,
            status
        ])
    
    return response

def generate_backlogs_csv(students):
    """Generate backlogs CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="backlogs_report_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Name', 'Branch', 'Semester', 'CGPA', 'Total Backlogs', 'Email'])
    
    for student in students:
        writer.writerow([
            student.student_id,
            student.name,
            student.get_branch_display(),
            student.current_semester,
            f"{student.cgpa:.2f}",
            student.total_backlogs,
            student.email
        ])
    
    return response

# Helper functions for PDF generation
def generate_students_pdf(students, title):
    """Generate PDF for students"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#8FB9A8'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Title
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Table data
    data = [['ID', 'Name', 'Branch', 'Sem', 'CGPA', 'Backlogs']]
    
    for student in students:
        data.append([
            student.student_id,
            student.name[:20],  # Truncate long names
            student.branch,
            str(student.current_semester),
            f"{student.cgpa:.2f}",
            str(student.total_backlogs)
        ])
    
    # Create table
    table = Table(data, colWidths=[1.5*inch, 2*inch, 1*inch, 0.6*inch, 0.8*inch, 0.8*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8FB9A8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Total Students: {students.count()}", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{title.lower().replace(" ", "_")}_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    return response

def generate_performance_pdf(students):
    """Generate performance PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#8FB9A8'),
        spaceAfter=30,
        alignment=1
    )
    
    elements.append(Paragraph("Performance Report", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Statistics
    excellent = students.filter(cgpa__gte=8.0).count()
    good = students.filter(cgpa__gte=6.5, cgpa__lt=8.0).count()
    average = students.filter(cgpa__gte=5.0, cgpa__lt=6.5).count()
    poor = students.filter(cgpa__lt=5.0).count()
    
    stats_data = [
        ['Performance Category', 'Count', 'Percentage'],
        ['Excellent (>= 8.0)', str(excellent), f"{(excellent/students.count()*100):.1f}%" if students.count() > 0 else '0%'],
        ['Good (6.5-7.9)', str(good), f"{(good/students.count()*100):.1f}%" if students.count() > 0 else '0%'],
        ['Average (5.0-6.4)', str(average), f"{(average/students.count()*100):.1f}%" if students.count() > 0 else '0%'],
        ['Need Attention (< 5.0)', str(poor), f"{(poor/students.count()*100):.1f}%" if students.count() > 0 else '0%'],
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 1*inch, 1.5*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8FB9A8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(stats_table)
    elements.append(Spacer(1, 30))
    
    # Student details
    data = [['ID', 'Name', 'Branch', 'CGPA', 'Status']]
    
    for student in students[:50]:  # Limit to 50 for PDF
        if student.cgpa >= 8.0:
            status = 'Excellent'
        elif student.cgpa >= 6.5:
            status = 'Good'
        elif student.cgpa >= 5.0:
            status = 'Average'
        else:
            status = 'Need Attention'
        
        data.append([
            student.student_id,
            student.name[:20],
            student.branch,
            f"{student.cgpa:.2f}",
            status
        ])
    
    table = Table(data, colWidths=[1.5*inch, 2*inch, 1*inch, 0.8*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FCB9AA')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(table)
    
    if students.count() > 50:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"Showing top 50 of {students.count()} students", styles['Italic']))
    
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="performance_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    return response

def generate_backlogs_pdf(students):
    """Generate backlogs PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#F1828D'),
        spaceAfter=30,
        alignment=1
    )
    
    elements.append(Paragraph("Students with Backlogs", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Table data
    data = [['ID', 'Name', 'Branch', 'Semester', 'CGPA', 'Backlogs']]
    
    for student in students:
        data.append([
            student.student_id,
            student.name[:20],
            student.branch,
            str(student.current_semester),
            f"{student.cgpa:.2f}",
            str(student.total_backlogs)
        ])
    
    table = Table(data, colWidths=[1.5*inch, 2*inch, 1*inch, 0.8*inch, 0.8*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1828D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Total Students with Backlogs: {students.count()}", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="backlogs_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    return response

# Branch Management Views
@login_required
def manage_branches(request):
    """Manage branches/departments"""
    branches = Branch.objects.all().order_by('code')
    
    context = {
        'branches': branches
    }
    
    return render(request, 'predictor/college/manage_branches.html', context)

@login_required
def add_branch(request):
    """Add a new branch"""
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        name = request.POST.get('name', '').strip()
        
        if code and name:
            if Branch.objects.filter(code=code).exists():
                messages.error(request, f'Branch with code {code} already exists')
            else:
                Branch.objects.create(code=code, name=name)
                messages.success(request, f'Branch {code} - {name} added successfully')
                return redirect('manage_branches')
        else:
            messages.error(request, 'Please provide both code and name')
    
    return redirect('manage_branches')

@login_required
def delete_branch(request, code):
    """Delete a branch"""
    branch = get_object_or_404(Branch, code=code)
    
    # Check if any students are using this branch
    student_count = StudentRecord.objects.filter(branch=code).count()
    
    if student_count > 0:
        messages.error(request, f'Cannot delete branch {code}. {student_count} students are enrolled in this branch.')
    else:
        branch.delete()
        messages.success(request, f'Branch {code} deleted successfully')
    
    return redirect('manage_branches')

