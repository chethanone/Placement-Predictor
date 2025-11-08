from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import StudentRecord, TrainingSession, SessionRecommendation


def student_sessions(request):
    """View all training sessions - student can enroll/unenroll"""
    # Get the logged-in student's USN from session
    student_usn = request.session.get('student_usn')
    
    if not student_usn:
        # Redirect to login if no session found
        messages.warning(request, 'Please enter your Student ID to access sessions.')
        return redirect('student_entry')
    
    # Get student record
    try:
        student = StudentRecord.objects.get(student_id=student_usn)
    except StudentRecord.DoesNotExist:
        messages.error(request, 'Student record not found.')
        return redirect('student_entry')
    
    # Get all active training sessions
    all_sessions = TrainingSession.objects.filter(
        is_active=True,
        scheduled_date__gte=timezone.now().date()
    ).order_by('scheduled_date', 'scheduled_time')
    
    # Get sessions student is enrolled in
    enrolled_session_ids = student.training_sessions.values_list('id', flat=True)
    
    # Get recommendations for this student
    recommendations = SessionRecommendation.objects.filter(
        student=student
    ).select_related('session')
    
    recommended_session_ids = [rec.session_id for rec in recommendations]
    
    # Build session data with enrollment status
    sessions_data = []
    for session in all_sessions:
        enrolled_count = session.registered_students.count()
        is_full = enrolled_count >= session.max_students
        is_enrolled = session.id in enrolled_session_ids
        is_recommended = session.id in recommended_session_ids
        
        # Get recommendation details if exists
        recommendation = None
        if is_recommended:
            recommendation = recommendations.filter(session=session).first()
        
        sessions_data.append({
            'session': session,
            'enrolled_count': enrolled_count,
            'seats_left': session.max_students - enrolled_count,
            'is_full': is_full,
            'is_enrolled': is_enrolled,
            'is_recommended': is_recommended,
            'recommendation': recommendation,
            'resource_list': session.resource_links.split(',') if session.resource_links else []
        })
    
    context = {
        'sessions': sessions_data,
        'student_usn': student_usn,
        'student_name': request.session.get('student_name', 'Student'),
    }
    
    return render(request, 'predictor/student/sessions.html', context)


def enroll_session(request, session_id):
    """Enroll student in a training session"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    student_usn = request.session.get('student_usn')
    if not student_usn:
        return JsonResponse({'success': False, 'message': 'Please login first'})
    
    try:
        student = StudentRecord.objects.get(student_id=student_usn)
        session = get_object_or_404(TrainingSession, id=session_id, is_active=True)
        
        # Check if already enrolled
        if student in session.registered_students.all():
            return JsonResponse({'success': False, 'message': 'Already enrolled in this session'})
        
        # Check if session is full
        if session.registered_students.count() >= session.max_students:
            return JsonResponse({'success': False, 'message': 'Session is full'})
        
        # Enroll the student
        session.registered_students.add(student)
        
        # Mark recommendation as registered if exists
        SessionRecommendation.objects.filter(
            student=student,
            session=session
        ).update(is_registered=True)
        
        enrolled_count = session.registered_students.count()
        seats_left = session.max_students - enrolled_count
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully enrolled in {session.title}',
            'enrolled_count': enrolled_count,
            'seats_left': seats_left
        })
        
    except StudentRecord.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Student record not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def unenroll_session(request, session_id):
    """Unenroll student from a training session"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    student_usn = request.session.get('student_usn')
    if not student_usn:
        return JsonResponse({'success': False, 'message': 'Please login first'})
    
    try:
        student = StudentRecord.objects.get(student_id=student_usn)
        session = get_object_or_404(TrainingSession, id=session_id, is_active=True)
        
        # Check if enrolled
        if student not in session.registered_students.all():
            return JsonResponse({'success': False, 'message': 'Not enrolled in this session'})
        
        # Check if session is too soon (e.g., within 24 hours)
        time_until_session = session.scheduled_date - timezone.now().date()
        if time_until_session.days < 1:
            return JsonResponse({
                'success': False,
                'message': 'Cannot unenroll less than 24 hours before session'
            })
        
        # Unenroll the student
        session.registered_students.remove(student)
        
        # Mark recommendation as not registered if exists
        SessionRecommendation.objects.filter(
            student=student,
            session=session
        ).update(is_registered=False)
        
        enrolled_count = session.registered_students.count()
        seats_left = session.max_students - enrolled_count
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully unenrolled from {session.title}',
            'enrolled_count': enrolled_count,
            'seats_left': seats_left
        })
        
    except StudentRecord.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Student record not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
