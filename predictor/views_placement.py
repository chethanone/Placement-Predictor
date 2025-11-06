"""
Placement Portal Views (Login Required)
View student scores and recommend training sessions
Includes new TPO dashboard with analytics and insights
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Avg, Count, Q, Sum, F
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch

from .models import (
    StudentRecord, StudentPrediction, TrainingSession, 
    SessionRecommendation, StudentQuiz, Company, EmployabilityScore,
    DepartmentAnalytics, Branch
)


def placement_login(request):
    """Placement portal login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('tpo_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'predictor/placement/login.html')


# ==================== TPO DASHBOARD ====================

@login_required
def tpo_dashboard(request):
    """Enhanced TPO Dashboard with comprehensive analytics"""
    # Overall Statistics
    total_students = StudentRecord.objects.filter(is_active=True).count()
    total_companies = Company.objects.filter(is_active=True).count()
    
    # Employability Scores
    employability_scores = EmployabilityScore.objects.all()
    excellent_count = employability_scores.filter(placement_readiness='excellent').count()
    good_count = employability_scores.filter(placement_readiness='good').count()
    average_count = employability_scores.filter(placement_readiness='average').count()
    needs_improvement_count = employability_scores.filter(placement_readiness='needs_improvement').count()
    
    overall_placement_readiness = (
        (excellent_count + good_count) / total_students * 100
    ) if total_students > 0 else 0
    
    avg_employability = employability_scores.aggregate(
        Avg('overall_employability')
    )['overall_employability__avg'] or 0
    
    # Top Department
    branch_data = []
    for branch in Branch.objects.filter(is_active=True):
        students = StudentRecord.objects.filter(branch=branch.code, is_active=True)
        if students.exists():
            avg_score = EmployabilityScore.objects.filter(
                student__branch=branch.code
            ).aggregate(Avg('overall_employability'))['overall_employability__avg'] or 0
            
            branch_data.append({
                'code': branch.code,
                'name': branch.name,
                'total_students': students.count(),
                'avg_employability': round(avg_score, 1),
                'placement_ready': EmployabilityScore.objects.filter(
                    student__branch=branch.code,
                    overall_employability__gte=70
                ).count()
            })
    
    # Sort by employability
    branch_data.sort(key=lambda x: x['avg_employability'], reverse=True)
    top_department = branch_data[0] if branch_data else None
    
    # Top Recruiters (companies with most placements)
    top_recruiters = Company.objects.filter(is_active=True).order_by('-total_placements')[:5]
    
    # Recent Activities
    recent_assessments = EmployabilityScore.objects.select_related('student').order_by('-last_assessed')[:10]
    
    # Skill Gap Analysis
    avg_skills = employability_scores.aggregate(
        communication=Avg('communication_score'),
        technical=Avg('technical_score'),
        coding=Avg('coding_score'),
        aptitude=Avg('aptitude_score'),
        soft_skills=Avg('soft_skills_score')
    )
    
    # Students Needing Attention (low employability)
    students_needing_attention = EmployabilityScore.objects.filter(
        overall_employability__lt=50
    ).select_related('student').order_by('overall_employability')[:10]
    
    context = {
        'total_students': total_students,
        'total_companies': total_companies,
        'overall_placement_readiness': round(overall_placement_readiness, 1),
        'avg_employability': round(avg_employability, 1),
        'excellent_count': excellent_count,
        'good_count': good_count,
        'average_count': average_count,
        'needs_improvement_count': needs_improvement_count,
        'top_department': top_department,
        'branch_data': branch_data,
        'top_recruiters': top_recruiters,
        'recent_assessments': recent_assessments,
        'avg_skills': avg_skills,
        'students_needing_attention': students_needing_attention,
    }
    
    return render(request, 'predictor/placement/tpo_dashboard.html', context)


# ==================== STUDENT MANAGEMENT ====================

@login_required
def student_list(request):
    """Student list with advanced filters and sorting"""
    students = StudentRecord.objects.filter(is_active=True).select_related()
    
    # Apply Filters
    branch = request.GET.get('branch')
    semester = request.GET.get('semester')
    min_cgpa = request.GET.get('min_cgpa')
    max_cgpa = request.GET.get('max_cgpa')
    employability_min = request.GET.get('employability_min')
    employability_max = request.GET.get('employability_max')
    placement_readiness = request.GET.get('placement_readiness')
    search = request.GET.get('search')
    
    if branch:
        students = students.filter(branch=branch)
    if semester:
        students = students.filter(current_semester=semester)
    if min_cgpa:
        students = students.filter(cgpa__gte=float(min_cgpa))
    if max_cgpa:
        students = students.filter(cgpa__lte=float(max_cgpa))
    if search:
        students = students.filter(
            Q(student_id__icontains=search) |
            Q(name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Get employability scores
    student_data = []
    for student in students:
        try:
            emp_score = EmployabilityScore.objects.get(student=student)
            
            # Apply employability filters
            if employability_min and emp_score.overall_employability < float(employability_min):
                continue
            if employability_max and emp_score.overall_employability > float(employability_max):
                continue
            if placement_readiness and emp_score.placement_readiness != placement_readiness:
                continue
            
            # Get latest prediction
            latest_prediction = StudentPrediction.objects.filter(student=student).order_by('-predicted_at').first()
            
            student_data.append({
                'student': student,
                'employability': emp_score,
                'placement_probability': latest_prediction.placement_probability if latest_prediction else 0
            })
        except EmployabilityScore.DoesNotExist:
            # Student without employability score
            if not employability_min and not employability_max and not placement_readiness:
                student_data.append({
                    'student': student,
                    'employability': None,
                    'placement_probability': 0
                })
    
    # Sorting
    sort_by = request.GET.get('sort_by', 'student_id')
    reverse = request.GET.get('order') == 'desc'
    
    if sort_by == 'employability':
        student_data.sort(key=lambda x: x['employability'].overall_employability if x['employability'] else 0, reverse=reverse)
    elif sort_by == 'cgpa':
        student_data.sort(key=lambda x: x['student'].cgpa, reverse=reverse)
    elif sort_by == 'name':
        student_data.sort(key=lambda x: x['student'].name, reverse=reverse)
    else:
        student_data.sort(key=lambda x: x['student'].student_id, reverse=reverse)
    
    # Pagination
    paginator = Paginator(student_data, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'branches': Branch.objects.filter(is_active=True),
        'filters': request.GET,
        'total_count': len(student_data)
    }
    
    return render(request, 'predictor/placement/student_list.html', context)


@login_required
def student_detail(request, student_id):
    """Detailed student profile with all information"""
    student = get_object_or_404(StudentRecord, student_id=student_id)
    
    # Get employability score
    try:
        employability = EmployabilityScore.objects.get(student=student)
    except EmployabilityScore.DoesNotExist:
        employability = None
    
    # Get predictions
    predictions = StudentPrediction.objects.filter(student=student).order_by('-predicted_at')
    latest_prediction = predictions.first()
    
    # Get marks
    marks = student.marks.select_related('subject').order_by('-semester', 'subject__subject_code')
    
    # Get recommendations
    recommendations = SessionRecommendation.objects.filter(student=student).select_related('session')
    
    # Get suitable companies
    suitable_companies = []
    if employability:
        suitable_companies = Company.objects.filter(
            is_active=True,
            min_cgpa__lte=student.cgpa,
            max_backlogs__gte=student.total_backlogs,
            technical_skills_min__lte=employability.technical_score,
            communication_skills_min__lte=employability.communication_score
        ).filter(
            Q(required_branches__icontains=student.branch) | Q(required_branches='')
        )
    
    context = {
        'student': student,
        'employability': employability,
        'latest_prediction': latest_prediction,
        'predictions': predictions,
        'marks': marks,
        'recommendations': recommendations,
        'suitable_companies': suitable_companies,
    }
    
    return render(request, 'predictor/placement/student_detail.html', context)


# ==================== AI RECOMMENDATIONS ====================

@login_required
def ai_recommendations(request):
    """AI-powered recommendations for students"""
    from django.contrib.auth.models import User
    
    # Get filter parameters
    selected_branch = request.GET.get('branch', '')
    employability_level = request.GET.get('employability_level', '')
    limit = int(request.GET.get('limit', 10))
    
    # Start with all employability scores
    employability_scores = EmployabilityScore.objects.select_related('student').all()
    
    # Apply filters
    if selected_branch:
        employability_scores = employability_scores.filter(student__branch=selected_branch)
    
    if employability_level:
        employability_scores = employability_scores.filter(placement_readiness=employability_level)
    
    # Limit results
    employability_scores = employability_scores[:limit]
    
    # Generate recommendations for each student
    recommendations = []
    for emp_score in employability_scores:
        student = emp_score.student
        
        # Analyze weaknesses and strengths
        ai_recs = []
        action_plan = []
        
        # Communication recommendations (personalized)
        if emp_score.communication_score < 4:
            ai_recs.append(f"{student.name}: Your communication score ({emp_score.communication_score}/10) needs urgent attention. Join Toastmasters or public speaking clubs immediately.")
            action_plan.append(f"Week 1-2: Attend daily communication workshop sessions and practice with peers")
        elif emp_score.communication_score < 6:
            ai_recs.append(f"{student.name}: Improve your communication from {emp_score.communication_score}/10 through group discussions and presentations in class.")
            action_plan.append(f"Next 3 weeks: Present 2 technical topics and participate in 5 group discussions")
        elif emp_score.communication_score < 8:
            ai_recs.append(f"{student.name}: Good communication ({emp_score.communication_score}/10)! Enhance it by volunteering for seminar presentations.")
            action_plan.append(f"This month: Lead one technical seminar and mentor 2 junior students")
        else:
            ai_recs.append(f"{student.name}: Excellent communication skills ({emp_score.communication_score}/10)! Lead campus events and corporate presentations.")
            action_plan.append(f"Immediate: Become club coordinator or event speaker")
        
        # Technical recommendations (personalized by branch)
        branch_tech = {
            'CSE': ['DSA', 'System Design', 'OOP', 'DBMS'],
            'ISE': ['Software Engineering', 'Cloud Computing', 'DevOps', 'Agile'],
            'ECE': ['Embedded Systems', 'IoT', 'Signal Processing', 'VLSI'],
            'ME': ['CAD/CAM', 'Thermodynamics', 'Manufacturing', 'AutoCAD'],
            'CE': ['Structural Analysis', 'AutoCAD Civil', 'Project Management', 'BIM'],
            'EEE': ['Power Systems', 'Control Systems', 'MATLAB', 'PLC Programming'],
            'AIML': ['ML Algorithms', 'Deep Learning', 'Python', 'TensorFlow']
        }
        tech_topics = branch_tech.get(student.branch, ['Core Concepts', 'Domain Knowledge'])
        
        if emp_score.technical_score < 5:
            ai_recs.append(f"{student.name}: Critical - Technical score is {emp_score.technical_score}/10. Master {tech_topics[0]} and {tech_topics[1]} within 4 weeks.")
            action_plan.append(f"Week 1-4: Complete Coursera/Udemy courses on {tech_topics[0]} and {tech_topics[1]}")
        elif emp_score.technical_score < 7:
            ai_recs.append(f"{student.name}: Technical skills at {emp_score.technical_score}/10. Focus on {tech_topics[2]} and build 2 mini-projects.")
            action_plan.append(f"Next 2 weeks: Study {tech_topics[2]} and implement 2 practical applications")
        elif emp_score.technical_score >= 8:
            ai_recs.append(f"{student.name}: Strong technical foundation ({emp_score.technical_score}/10)! Explore {tech_topics[3]} and contribute to open-source.")
            action_plan.append(f"This month: Make 3 GitHub contributions in {tech_topics[3]} domain")
        
        # Coding recommendations (personalized with platforms)
        platforms = ['LeetCode', 'HackerRank', 'CodeChef', 'Codeforces', 'GeeksforGeeks']
        selected_platform = platforms[hash(student.student_id) % len(platforms)]
        
        if emp_score.coding_score < 5:
            ai_recs.append(f"{student.name}: Coding skills ({emp_score.coding_score}/10) need immediate work. Start with {selected_platform} Easy problems - solve 3 daily.")
            action_plan.append(f"Daily for 4 weeks: Solve 3 Easy + 1 Medium problem on {selected_platform}")
        elif emp_score.coding_score < 7:
            ai_recs.append(f"{student.name}: Boost coding from {emp_score.coding_score}/10 by solving Medium problems on {selected_platform} - target 5/week.")
            action_plan.append(f"Weekly goal: Complete 5 Medium problems and 1 Hard problem on {selected_platform}")
        elif emp_score.coding_score >= 8:
            ai_recs.append(f"{student.name}: Excellent coding ({emp_score.coding_score}/10)! Participate in weekly {selected_platform} contests and hackathons.")
            action_plan.append(f"Next 2 months: Participate in 8 coding contests and 2 hackathons")
        
        # Aptitude recommendations (personalized with specific areas)
        aptitude_areas = ['Quantitative', 'Logical Reasoning', 'Verbal Ability', 'Data Interpretation']
        focus_area = aptitude_areas[hash(student.email) % len(aptitude_areas)]
        
        if emp_score.aptitude_score < 50:
            ai_recs.append(f"{student.name}: Aptitude score ({emp_score.aptitude_score}/100) is critical! Focus on {focus_area} - practice 50 questions daily.")
            action_plan.append(f"Daily routine: 50 {focus_area} questions + 2 full mock tests per week")
        elif emp_score.aptitude_score < 70:
            ai_recs.append(f"{student.name}: Improve aptitude from {emp_score.aptitude_score}/100 by mastering {focus_area} and taking weekly mock tests.")
            action_plan.append(f"Weekly: Practice 200+ {focus_area} questions and attempt 3 timed tests")
        elif emp_score.aptitude_score >= 80:
            ai_recs.append(f"{student.name}: Strong aptitude ({emp_score.aptitude_score}/100)! Maintain consistency and help peers in {focus_area}.")
            action_plan.append(f"Ongoing: Take 2 company-specific mock tests weekly and mentor classmates")
        
        # Soft skills recommendations (personalized)
        if emp_score.soft_skills_score < 6:
            ai_recs.append(f"{student.name}: Soft skills ({emp_score.soft_skills_score}/10) need development. Join {student.current_semester}th sem group projects actively.")
            action_plan.append(f"This semester: Lead 1 group project and participate in 3 extracurriculars")
        elif emp_score.soft_skills_score >= 8:
            ai_recs.append(f"{student.name}: Excellent soft skills ({emp_score.soft_skills_score}/10)! Mentor juniors and coordinate placement activities.")
            action_plan.append(f"This month: Mentor 3 junior students and organize 1 workshop")
        
        # Projects and internships (personalized with counts)
        if emp_score.projects_count == 0:
            ai_recs.append(f"{student.name}: No projects yet! Start with 1 {student.branch}-specific project using trending tech this week.")
            action_plan.append(f"Next 3 weeks: Build and deploy 1 complete {student.branch} project on GitHub")
        elif emp_score.projects_count < 2:
            ai_recs.append(f"{student.name}: You have {emp_score.projects_count} project(s). Add 2 more diverse projects to strengthen your portfolio.")
            action_plan.append(f"Next month: Complete 2 industry-relevant projects with documentation")
        
        if emp_score.internships_count == 0:
            ai_recs.append(f"{student.name}: No internship experience. Apply to 15+ positions on Internshala/LinkedIn for {student.branch} roles immediately.")
            action_plan.append(f"This week: Apply to 15 internships + prepare 2-page resume highlighting projects")
        
        # Overall employability recommendations (personalized by CGPA and score)
        if emp_score.overall_employability < 40:
            ai_recs.append(f"{student.name}: Urgent - Overall readiness is {emp_score.overall_employability}% with CGPA {student.cgpa}. Intensive 6-week improvement plan needed.")
            action_plan.append(f"Week 1: One-on-one counseling with TPO to create personalized roadmap")
        elif emp_score.overall_employability < 60:
            ai_recs.append(f"{student.name}: At {emp_score.overall_employability}% readiness (CGPA: {student.cgpa}), you need consistent effort across all areas for 4 weeks.")
            action_plan.append(f"Month-long plan: Daily skill practice + weekly progress review with mentor")
        elif emp_score.overall_employability >= 75:
            ai_recs.append(f"{student.name}: Excellent preparation at {emp_score.overall_employability}% (CGPA: {student.cgpa})! Focus on interviews and company applications.")
            action_plan.append(f"Next 2 weeks: Attend 4 mock interviews + apply to 20 target companies")
        
        # Add specific company recommendations based on profile (personalized)
        if emp_score.overall_employability >= 80 and student.cgpa >= 8.0:
            action_plan.append(f"Target Profile: Top-tier (Google, Microsoft, Amazon, Adobe) - Batch {student.batch_year}")
        elif emp_score.overall_employability >= 70 and student.cgpa >= 7.5:
            action_plan.append(f"Target Profile: Product MNCs (Flipkart, Oracle, SAP, Cisco) - Batch {student.batch_year}")
        elif emp_score.overall_employability >= 60 and student.cgpa >= 7.0:
            action_plan.append(f"Target Profile: Mid-tier companies (Infosys, TCS Digital, Cognizant) - Batch {student.batch_year}")
        else:
            action_plan.append(f"Target Profile: Service companies, startups for experience - Batch {student.batch_year}")
        
        # Determine readiness class for styling
        if emp_score.overall_employability >= 90:
            readiness_class = 'excellent'
        elif emp_score.overall_employability >= 70:
            readiness_class = 'good'
        elif emp_score.overall_employability >= 50:
            readiness_class = 'average'
        else:
            readiness_class = 'poor'
        
        recommendations.append({
            'student': student,
            'employability_score': emp_score.overall_employability,
            'communication_score': emp_score.communication_score,
            'technical_score': emp_score.technical_score,
            'coding_score': emp_score.coding_score,
            'aptitude_score': emp_score.aptitude_score,
            'soft_skills_score': emp_score.soft_skills_score,
            'projects_count': emp_score.projects_count,
            'internships_count': emp_score.internships_count,
            'ai_recommendations': ai_recs[:5],  # Top 5 recommendations
            'action_plan': action_plan[:4],  # Top 4 action items
            'readiness_class': readiness_class,
        })
    
    # Get all branches for filter
    branches = Branch.objects.filter(is_active=True)
    
    context = {
        'recommendations': recommendations,
        'branches': branches,
        'selected_branch': selected_branch,
        'employability_level': employability_level,
        'limit': limit,
    }
    
    return render(request, 'predictor/placement/ai_recommendations.html', context)


@login_required
def ai_recommendations_old(request):
    """AI-powered recommendations using Gemini API"""
    import google.generativeai as genai
    import os
    from django.conf import settings
    import json
    
    # Get or generate recommendations
    ai_insights = None
    error_message = None
    generating = False
    
    if request.method == 'POST':
        generating = True
        
        # Get Gemini API key from environment or settings
        api_key = os.environ.get('GEMINI_API_KEY') or getattr(settings, 'GEMINI_API_KEY', None)
        
        if not api_key:
            error_message = "Gemini API key not configured. Please set GEMINI_API_KEY in environment variables."
        else:
            try:
                # Configure Gemini
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')
                
                # Gather student data
                total_students = StudentRecord.objects.filter(is_active=True).count()
                employability_scores = EmployabilityScore.objects.all()
                
                # Calculate statistics
                avg_scores = employability_scores.aggregate(
                    communication=Avg('communication_score'),
                    technical=Avg('technical_score'),
                    coding=Avg('coding_score'),
                    aptitude=Avg('aptitude_score'),
                    soft_skills=Avg('soft_skills_score'),
                    overall=Avg('overall_employability')
                )
                
                # Get readiness distribution
                excellent = employability_scores.filter(placement_readiness='excellent').count()
                good = employability_scores.filter(placement_readiness='good').count()
                average = employability_scores.filter(placement_readiness='average').count()
                needs_improvement = employability_scores.filter(placement_readiness='needs_improvement').count()
                
                # Department-wise data
                dept_data = []
                for branch in Branch.objects.filter(is_active=True):
                    scores = EmployabilityScore.objects.filter(student__branch=branch.code)
                    if scores.exists():
                        dept_avg = scores.aggregate(
                            comm=Avg('communication_score'),
                            tech=Avg('technical_score'),
                            code=Avg('coding_score'),
                            apt=Avg('aptitude_score'),
                            soft=Avg('soft_skills_score')
                        )
                        dept_data.append({
                            'name': branch.name,
                            'count': scores.count(),
                            'scores': dept_avg
                        })
                
                # Create prompt for Gemini
                prompt = f"""
                As a College Training & Placement Officer AI Assistant, analyze this placement data and provide comprehensive, actionable recommendations:

                OVERALL STATISTICS:
                - Total Active Students: {total_students}
                - Students with Assessments: {employability_scores.count()}
                
                AVERAGE SCORES (out of 10, aptitude out of 100):
                - Communication: {avg_scores['communication']:.1f}/10
                - Technical Skills: {avg_scores['technical']:.1f}/10
                - Coding Skills: {avg_scores['coding']:.1f}/10
                - Aptitude: {avg_scores['aptitude']:.1f}/100
                - Soft Skills: {avg_scores['soft_skills']:.1f}/10
                - Overall Employability: {avg_scores['overall']:.1f}%
                
                PLACEMENT READINESS DISTRIBUTION:
                - Excellent (90-100%): {excellent} students
                - Good (70-89%): {good} students
                - Average (50-69%): {average} students
                - Needs Improvement (<50%): {needs_improvement} students
                
                DEPARTMENT-WISE DATA:
                {json.dumps(dept_data, indent=2)}

                Provide recommendations in the following JSON format:
                {{
                    "executive_summary": "Brief 2-3 sentence overview of the placement readiness",
                    "key_strengths": ["strength1", "strength2", "strength3"],
                    "areas_of_concern": ["concern1", "concern2", "concern3"],
                    "priority_actions": [
                        {{"action": "action title", "description": "detailed description", "priority": "High/Medium/Low", "target": "number of students affected"}},
                    ],
                    "training_recommendations": [
                        {{"title": "Training session title", "focus_areas": ["area1", "area2"], "duration": "suggested duration", "target_students": "description"}},
                    ],
                    "department_insights": [
                        {{"department": "dept name", "insight": "specific insight", "recommendation": "specific action"}},
                    ],
                    "success_strategies": ["strategy1", "strategy2", "strategy3"],
                    "timeline_suggestion": "Suggested timeline for implementing recommendations"
                }}
                
                Make recommendations specific, actionable, and data-driven. Focus on practical steps the TPO can implement.
                """
                
                # Generate recommendations
                response = model.generate_content(prompt)
                
                # Parse response
                response_text = response.text.strip()
                
                # Extract JSON from markdown code blocks if present
                if '```json' in response_text:
                    response_text = response_text.split('```json')[1].split('```')[0].strip()
                elif '```' in response_text:
                    response_text = response_text.split('```')[1].split('```')[0].strip()
                
                ai_insights = json.loads(response_text)
                
            except json.JSONDecodeError as e:
                error_message = f"Error parsing AI response. Please try again."
                print(f"JSON Error: {e}")
                print(f"Response: {response_text}")
            except Exception as e:
                error_message = f"Error generating recommendations: {str(e)}"
                print(f"Error: {e}")
    
    # Get students needing specific training
    weak_communication = EmployabilityScore.objects.filter(
        communication_score__lt=6
    ).select_related('student').order_by('communication_score')[:10]
    
    weak_technical = EmployabilityScore.objects.filter(
        technical_score__lt=6
    ).select_related('student').order_by('technical_score')[:10]
    
    weak_coding = EmployabilityScore.objects.filter(
        coding_score__lt=6
    ).select_related('student').order_by('coding_score')[:10]
    
    weak_aptitude = EmployabilityScore.objects.filter(
        aptitude_score__lt=50
    ).select_related('student').order_by('aptitude_score')[:10]
    
    # Department-wise statistics
    dept_stats = []
    for branch in Branch.objects.filter(is_active=True):
        scores = EmployabilityScore.objects.filter(student__branch=branch.code)
        if scores.exists():
            avg_scores = scores.aggregate(
                communication=Avg('communication_score'),
                technical=Avg('technical_score'),
                coding=Avg('coding_score'),
                aptitude=Avg('aptitude_score'),
                soft_skills=Avg('soft_skills_score'),
                overall=Avg('overall_employability')
            )
            
            dept_stats.append({
                'branch': branch,
                'avg_scores': avg_scores,
                'student_count': scores.count(),
                'ready_count': scores.filter(overall_employability__gte=70).count()
            })
    
    context = {
        'ai_insights': ai_insights,
        'error_message': error_message,
        'generating': generating,
        'weak_communication': weak_communication,
        'weak_technical': weak_technical,
        'weak_coding': weak_coding,
        'weak_aptitude': weak_aptitude,
        'dept_stats': dept_stats,
        'total_students': StudentRecord.objects.filter(is_active=True).count(),
        'assessed_students': EmployabilityScore.objects.count(),
    }
    
    return render(request, 'predictor/placement/ai_recommendations.html', context)


@login_required
def what_if_simulation(request):
    """What-if analysis: show impact of skill improvements"""
    result = None
    
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_object_or_404(StudentRecord, student_id=student_id)
        
        try:
            current_emp = EmployabilityScore.objects.get(student=student)
            
            # Get improvement values
            communication_improvement = float(request.POST.get('communication_improvement', 0))
            technical_improvement = float(request.POST.get('technical_improvement', 0))
            coding_improvement = float(request.POST.get('coding_improvement', 0))
            aptitude_improvement = float(request.POST.get('aptitude_improvement', 0))
            projects_add = int(request.POST.get('projects_add', 0))
            internships_add = int(request.POST.get('internships_add', 0))
            
            # Calculate new scores
            new_communication = min(current_emp.communication_score + communication_improvement, 10)
            new_technical = min(current_emp.technical_score + technical_improvement, 10)
            new_coding = min(current_emp.coding_score + coding_improvement, 10)
            new_aptitude = min(current_emp.aptitude_score + aptitude_improvement, 100)
            new_projects = current_emp.projects_count + projects_add
            new_internships = current_emp.internships_count + internships_add
            
            # Calculate new employability score
            new_score = (
                new_communication * 0.15 * 10 +
                new_technical * 0.25 * 10 +
                new_aptitude * 0.15 +
                new_coding * 0.20 * 10 +
                current_emp.soft_skills_score * 0.10 * 10 +
                (student.cgpa / 10) * 0.10 * 100 +
                min(new_projects * 2, 5) +
                min(new_internships * 3, 5) +
                min(current_emp.certifications_count * 1, 3) +
                min(current_emp.hackathons_count * 2, 3)
            )
            new_score = min(new_score, 100)
            
            # Calculate improvement
            improvement = new_score - current_emp.overall_employability
            
            # Find new suitable companies
            new_suitable_companies = Company.objects.filter(
                is_active=True,
                min_cgpa__lte=student.cgpa,
                max_backlogs__gte=student.total_backlogs,
                technical_skills_min__lte=new_technical,
                communication_skills_min__lte=new_communication
            ).filter(
                Q(required_branches__icontains=student.branch) | Q(required_branches='')
            )
            
            current_suitable_companies = Company.objects.filter(
                is_active=True,
                min_cgpa__lte=student.cgpa,
                max_backlogs__gte=student.total_backlogs,
                technical_skills_min__lte=current_emp.technical_score,
                communication_skills_min__lte=current_emp.communication_score
            ).filter(
                Q(required_branches__icontains=student.branch) | Q(required_branches='')
            )
            
            result = {
                'student': student,
                'current_score': round(current_emp.overall_employability, 1),
                'new_score': round(new_score, 1),
                'improvement': round(improvement, 1),
                'current_companies_count': current_suitable_companies.count(),
                'new_companies_count': new_suitable_companies.count(),
                'additional_companies': new_suitable_companies.count() - current_suitable_companies.count(),
                'current_readiness': current_emp.get_placement_readiness_display(),
                'new_readiness': 'Excellent' if new_score >= 90 else 'Good' if new_score >= 70 else 'Average' if new_score >= 50 else 'Needs Improvement',
            }
        except EmployabilityScore.DoesNotExist:
            messages.error(request, 'Employability score not found for this student')
    
    # Get all students for dropdown
    students = StudentRecord.objects.filter(is_active=True).order_by('student_id')
    
    context = {
        'students': students,
        'result': result
    }
    
    return render(request, 'predictor/placement/what_if_simulation.html', context)


# ==================== COMPANY-STUDENT FIT ====================

@login_required
def company_student_fit(request):
    """Visual matrix showing student-company compatibility"""
    # Get filter parameters
    company_type = request.GET.get('company_type')
    branch = request.GET.get('branch')
    
    # Get companies
    companies = Company.objects.filter(is_active=True)
    if company_type:
        companies = companies.filter(company_type=company_type)
    
    companies = companies[:10]  # Limit to 10 for display
    
    # Get students
    students = StudentRecord.objects.filter(is_active=True)
    if branch:
        students = students.filter(branch=branch)
    
    students = students[:20]  # Limit to 20 for display
    
    # Build compatibility matrix
    matrix = []
    total_matches = 0
    
    for student in students:
        try:
            emp_score = EmployabilityScore.objects.get(student=student)
            row = {
                'student': student,
                'employability': emp_score.overall_employability,
                'compatibility': []
            }
            
            for company in companies:
                # Check compatibility
                is_compatible = (
                    student.cgpa >= company.min_cgpa and
                    student.total_backlogs <= company.max_backlogs and
                    emp_score.technical_score >= company.technical_skills_min and
                    emp_score.communication_score >= company.communication_skills_min and
                    emp_score.aptitude_score >= company.aptitude_score_min
                )
                
                # Check branch requirement
                if company.required_branches:
                    required_branch_list = [b.strip() for b in company.required_branches.split(',')]
                    if student.branch not in required_branch_list:
                        is_compatible = False
                
                # Calculate match percentage
                match_score = 0
                if is_compatible:
                    cgpa_score = (student.cgpa / 10) * 20
                    tech_score = (emp_score.technical_score / 10) * 30
                    comm_score = (emp_score.communication_score / 10) * 20
                    apt_score = (emp_score.aptitude_score / 100) * 20
                    exp_score = min((emp_score.projects_count + emp_score.internships_count) * 2, 10)
                    
                    match_score = cgpa_score + tech_score + comm_score + apt_score + exp_score
                    total_matches += 1
                
                row['compatibility'].append({
                    'company': company,
                    'is_compatible': is_compatible,
                    'match_score': round(match_score, 1)
                })
            
            matrix.append(row)
        except EmployabilityScore.DoesNotExist:
            continue
    
    context = {
        'matrix': matrix,
        'companies': companies,
        'branches': Branch.objects.filter(is_active=True),
        'company_types': Company.COMPANY_TYPES,
        'filters': request.GET,
        'total_matches': total_matches,
    }
    
    return render(request, 'predictor/placement/company_student_fit.html', context)


# ==================== DATA MANAGEMENT ====================

@login_required
def data_management(request):
    """Data import/export and bulk operations"""
    context = {
        'total_students': StudentRecord.objects.count(),
        'total_assessments': EmployabilityScore.objects.count(),
        'total_companies': Company.objects.count(),
    }
    
    return render(request, 'predictor/placement/data_management.html', context)


@login_required
def import_student_data(request):
    """Import student data from CSV"""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            created_count = 0
            updated_count = 0
            errors = []
            
            for row in reader:
                try:
                    student_id = row.get('student_id') or row.get('Student ID')
                    name = row.get('name') or row.get('Name')
                    email = row.get('email') or row.get('Email')
                    branch = row.get('branch') or row.get('Branch')
                    cgpa = float(row.get('cgpa') or row.get('CGPA') or 0)
                    
                    student, created = StudentRecord.objects.update_or_create(
                        student_id=student_id,
                        defaults={
                            'name': name,
                            'email': email,
                            'branch': branch,
                            'cgpa': cgpa,
                            'phone': row.get('phone', ''),
                            'current_semester': int(row.get('semester', 1)),
                            'batch_year': int(row.get('batch_year', 2021)),
                            'total_backlogs': int(row.get('backlogs', 0)),
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                        
                except Exception as e:
                    errors.append(f"Error processing row {student_id}: {str(e)}")
            
            messages.success(request, f'Successfully imported {created_count} new students and updated {updated_count} existing students')
            if errors:
                for error in errors[:5]:  # Show first 5 errors
                    messages.warning(request, error)
            
        except Exception as e:
            messages.error(request, f'Error reading CSV file: {str(e)}')
        
        return redirect('data_management')
    
    return render(request, 'predictor/placement/import_students.html')


@login_required
def export_student_data(request):
    """Export student data to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Name', 'Email', 'Branch', 'CGPA', 'Semester', 'Backlogs', 'Phone', 'Employability Score', 'Placement Readiness'])
    
    students = StudentRecord.objects.filter(is_active=True)
    for student in students:
        try:
            emp = EmployabilityScore.objects.get(student=student)
            emp_score = round(emp.overall_employability, 1)
            readiness = emp.get_placement_readiness_display()
        except EmployabilityScore.DoesNotExist:
            emp_score = 'N/A'
            readiness = 'N/A'
        
        writer.writerow([
            student.student_id,
            student.name,
            student.email,
            student.get_branch_display(),
            student.cgpa,
            student.current_semester,
            student.total_backlogs,
            student.phone,
            emp_score,
            readiness
        ])
    
    return response


# ==================== REPORTS ====================

@login_required
def generate_department_report(request):
    """Generate comprehensive department report"""
    branch_code = request.GET.get('branch')
    
    if not branch_code:
        branches = Branch.objects.filter(is_active=True)
        context = {'branches': branches}
        return render(request, 'predictor/placement/select_department.html', context)
    
    branch = get_object_or_404(Branch, code=branch_code)
    students = StudentRecord.objects.filter(branch=branch_code, is_active=True)
    
    # Statistics
    total_students = students.count()
    avg_cgpa = students.aggregate(Avg('cgpa'))['cgpa__avg'] or 0
    
    emp_scores = EmployabilityScore.objects.filter(student__branch=branch_code)
    avg_employability = emp_scores.aggregate(Avg('overall_employability'))['overall_employability__avg'] or 0
    
    placement_ready = emp_scores.filter(overall_employability__gte=70).count()
    placement_ready_percent = (placement_ready / total_students * 100) if total_students > 0 else 0
    
    # Skill averages
    avg_skills = emp_scores.aggregate(
        communication=Avg('communication_score'),
        technical=Avg('technical_score'),
        coding=Avg('coding_score'),
        aptitude=Avg('aptitude_score'),
        soft_skills=Avg('soft_skills_score')
    )
    
    # Generate PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#6d28d9'),
        spaceAfter=30,
        alignment=1
    )
    elements.append(Paragraph(f'{branch.name} - Placement Report', title_style))
    elements.append(Spacer(1, 20))
    
    # Summary Statistics
    summary_data = [
        ['Metric', 'Value'],
        ['Total Students', str(total_students)],
        ['Average CGPA', f'{avg_cgpa:.2f}'],
        ['Average Employability', f'{avg_employability:.1f}%'],
        ['Placement Ready (>70%)', f'{placement_ready} ({placement_ready_percent:.1f}%)'],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6d28d9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 30))
    
    # Skill Analysis
    elements.append(Paragraph('Skill Analysis', styles['Heading2']))
    elements.append(Spacer(1, 10))
    
    skill_data = [
        ['Skill', 'Average Score'],
        ['Communication', f'{avg_skills["communication"]:.1f}/10'],
        ['Technical', f'{avg_skills["technical"]:.1f}/10'],
        ['Coding', f'{avg_skills["coding"]:.1f}/10'],
        ['Aptitude', f'{avg_skills["aptitude"]:.1f}/100'],
        ['Soft Skills', f'{avg_skills["soft_skills"]:.1f}/10'],
    ]
    
    skill_table = Table(skill_data, colWidths=[3*inch, 2*inch])
    skill_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#a855f7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(skill_table)
    
    # Build PDF
    doc.build(elements)
    
    # Return PDF response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{branch_code}_placement_report.pdf"'
    
    return response


# ==================== OLD VIEWS (Keep for compatibility) ====================

@login_required
def placement_dashboard(request):
    """Old placement dashboard - redirect to new TPO dashboard"""
    return redirect('tpo_dashboard')


@login_required
def placement_analytics(request):
    """Detailed analytics and visualizations"""
    # CGPA distribution
    cgpa_ranges = [
        ('9.0-10.0', StudentRecord.objects.filter(cgpa__gte=9.0).count()),
        ('8.0-8.9', StudentRecord.objects.filter(cgpa__gte=8.0, cgpa__lt=9.0).count()),
        ('7.0-7.9', StudentRecord.objects.filter(cgpa__gte=7.0, cgpa__lt=8.0).count()),
        ('6.0-6.9', StudentRecord.objects.filter(cgpa__gte=6.0, cgpa__lt=7.0).count()),
        ('Below 6.0', StudentRecord.objects.filter(cgpa__lt=6.0).count()),
    ]
    
    # Placement probability distribution
    prob_ranges = [
        ('90-100%', StudentPrediction.objects.filter(placement_probability__gte=90).count()),
        ('70-89%', StudentPrediction.objects.filter(placement_probability__gte=70, placement_probability__lt=90).count()),
        ('50-69%', StudentPrediction.objects.filter(placement_probability__gte=50, placement_probability__lt=70).count()),
        ('Below 50%', StudentPrediction.objects.filter(placement_probability__lt=50).count()),
    ]
    
    # Skills distribution
    predictions = StudentPrediction.objects.all()
    avg_communication = predictions.aggregate(Avg('communication_skills'))['communication_skills__avg'] or 0
    avg_technical = predictions.aggregate(Avg('technical_skills'))['technical_skills__avg'] or 0
    avg_aptitude = predictions.aggregate(Avg('aptitude_score'))['aptitude_score__avg'] or 0
    
    context = {
        'cgpa_ranges': cgpa_ranges,
        'prob_ranges': prob_ranges,
        'avg_communication': round(avg_communication, 1),
        'avg_technical': round(avg_technical, 1),
        'avg_aptitude': round(avg_aptitude, 1),
        'total_students': StudentRecord.objects.count(),
        'total_predictions': predictions.count()
    }
    
    return render(request, 'predictor/placement/analytics.html', context)


# ==================== TRAINING SESSION MANAGEMENT ====================

@login_required
def manage_training_sessions(request):
    """List all training sessions"""
    sessions = TrainingSession.objects.all().order_by('-scheduled_date')
    
    # Filter by type
    session_type = request.GET.get('type')
    if session_type:
        sessions = sessions.filter(session_type=session_type)
    
    context = {
        'sessions': sessions,
        'session_types': TrainingSession.SESSION_TYPES
    }
    
    return render(request, 'predictor/placement/manage_sessions.html', context)


@login_required
def add_training_session(request):
    """Add new training session"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        session_type = request.POST.get('session_type')
        scheduled_date = request.POST.get('scheduled_date')
        scheduled_time = request.POST.get('scheduled_time')
        duration_minutes = request.POST.get('duration_minutes', 60)
        venue = request.POST.get('venue')
        max_students = request.POST.get('max_students', 50)
        resource_links = request.POST.get('resource_links', '')
        
        try:
            session = TrainingSession.objects.create(
                title=title,
                description=description,
                session_type=session_type,
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
                duration_minutes=duration_minutes,
                venue=venue,
                max_students=max_students,
                resource_links=resource_links,
                created_by=request.user
            )
            messages.success(request, f'Training session "{title}" created successfully!')
            return redirect('manage_training_sessions')
        except Exception as e:
            messages.error(request, f'Error creating session: {str(e)}')
    
    context = {
        'session_types': TrainingSession.SESSION_TYPES
    }
    
    return render(request, 'predictor/placement/add_session.html', context)


@login_required
def edit_training_session(request, session_id):
    """Edit training session"""
    session = get_object_or_404(TrainingSession, id=session_id)
    
    if request.method == 'POST':
        session.title = request.POST.get('title')
        session.description = request.POST.get('description')
        session.session_type = request.POST.get('session_type')
        session.scheduled_date = request.POST.get('scheduled_date')
        session.scheduled_time = request.POST.get('scheduled_time')
        session.duration_minutes = request.POST.get('duration_minutes')
        session.venue = request.POST.get('venue')
        session.max_students = request.POST.get('max_students')
        session.resource_links = request.POST.get('resource_links', '')
        session.is_active = request.POST.get('is_active') == 'on'
        
        try:
            session.save()
            messages.success(request, f'Training session "{session.title}" updated successfully!')
            return redirect('manage_training_sessions')
        except Exception as e:
            messages.error(request, f'Error updating session: {str(e)}')
    
    context = {
        'session': session,
        'session_types': TrainingSession.SESSION_TYPES
    }
    
    return render(request, 'predictor/placement/edit_session.html', context)


@login_required
def delete_training_session(request, session_id):
    """Delete training session"""
    session = get_object_or_404(TrainingSession, id=session_id)
    
    if request.method == 'POST':
        title = session.title
        session.delete()
        messages.success(request, f'Training session "{title}" deleted successfully!')
        return redirect('manage_training_sessions')
    
    context = {'session': session}
    return render(request, 'predictor/placement/delete_session_confirm.html', context)


@login_required
def placement_logout(request):
    """Logout"""
    logout(request)
    return redirect('placement_login')

    """Placement portal login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('placement_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'predictor/placement/login.html')

@login_required
def placement_dashboard(request):
    """Placement dashboard with analytics"""
    total_students = StudentRecord.objects.count()
    predictions = StudentPrediction.objects.all()
    
    # Calculate placement statistics
    total_predictions = predictions.count()
    placed_predictions = predictions.filter(placement_probability__gte=60).count()
    placement_rate = (placed_predictions / total_predictions * 100) if total_predictions > 0 else 0
    
    # Average scores
    avg_cgpa = StudentRecord.objects.aggregate(Avg('cgpa'))['cgpa__avg'] or 0
    avg_placement_prob = predictions.aggregate(Avg('placement_probability'))['placement_probability__avg'] or 0
    
    # Branch-wise placement rate
    branch_stats = []
    for branch_code, branch_name in StudentRecord.BRANCH_CHOICES:
        students = StudentRecord.objects.filter(branch=branch_code)
        preds = StudentPrediction.objects.filter(student__branch=branch_code)
        placed = preds.filter(placement_probability__gte=60).count()
        total = preds.count()
        rate = (placed / total * 100) if total > 0 else 0
        
        branch_stats.append({
            'branch': branch_name,
            'total': students.count(),
            'placement_rate': round(rate, 1)
        })
    
    context = {
        'total_students': total_students,
        'placement_rate': round(placement_rate, 1),
        'avg_cgpa': round(avg_cgpa, 2),
        'avg_placement_prob': round(avg_placement_prob, 1),
        'branch_stats': branch_stats,
        'recent_predictions': predictions.order_by('-predicted_at')[:10]
    }
    
    return render(request, 'predictor/placement/dashboard.html', context)

@login_required
def view_student(request, student_id):
    """View detailed student profile"""
    student = get_object_or_404(StudentRecord, student_id=student_id)
    
    # Get all related data
    predictions = StudentPrediction.objects.filter(student=student)
    quizzes = StudentQuiz.objects.filter(student_id=student_id)
    marks = student.marks.all()
    recommendations = SessionRecommendation.objects.filter(student=student)
    
    context = {
        'student': student,
        'predictions': predictions,
        'quizzes': quizzes,
        'marks': marks,
        'recommendations': recommendations
    }
    
    return render(request, 'predictor/placement/student_profile.html', context)

@login_required
def recommend_session(request, student_id):
    """Recommend training session to student"""
    student = get_object_or_404(StudentRecord, student_id=student_id)
    
    if request.method == 'POST':
        session_id = request.POST.get('session')
        reason = request.POST.get('reason')
        priority = request.POST.get('priority')
        
        session = TrainingSession.objects.get(id=session_id)
        
        # Create recommendation
        recommendation = SessionRecommendation.objects.create(
            student=student,
            session=session,
            reason=reason,
            priority=priority
        )
        
        messages.success(request, f'Training session recommended to {student.name}!')
        return redirect('view_student', student_id=student_id)
    
    # Get available sessions
    sessions = TrainingSession.objects.filter(is_active=True)
    
    context = {
        'student': student,
        'sessions': sessions
    }
    
    return render(request, 'predictor/placement/recommend_session.html', context)

@login_required
def placement_analytics(request):
    """Detailed analytics and visualizations"""
    # CGPA distribution
    cgpa_ranges = [
        ('9.0-10.0', StudentRecord.objects.filter(cgpa__gte=9.0).count()),
        ('8.0-8.9', StudentRecord.objects.filter(cgpa__gte=8.0, cgpa__lt=9.0).count()),
        ('7.0-7.9', StudentRecord.objects.filter(cgpa__gte=7.0, cgpa__lt=8.0).count()),
        ('6.0-6.9', StudentRecord.objects.filter(cgpa__gte=6.0, cgpa__lt=7.0).count()),
        ('Below 6.0', StudentRecord.objects.filter(cgpa__lt=6.0).count()),
    ]
    
    # Placement probability distribution
    prob_ranges = [
        ('90-100%', StudentPrediction.objects.filter(placement_probability__gte=90).count()),
        ('70-89%', StudentPrediction.objects.filter(placement_probability__gte=70, placement_probability__lt=90).count()),
        ('50-69%', StudentPrediction.objects.filter(placement_probability__gte=50, placement_probability__lt=70).count()),
        ('Below 50%', StudentPrediction.objects.filter(placement_probability__lt=50).count()),
    ]
    
    # Skills distribution
    predictions = StudentPrediction.objects.all()
    avg_communication = predictions.aggregate(Avg('communication_skills'))['communication_skills__avg'] or 0
    avg_technical = predictions.aggregate(Avg('technical_skills'))['technical_skills__avg'] or 0
    avg_aptitude = predictions.aggregate(Avg('aptitude_score'))['aptitude_score__avg'] or 0
    
    context = {
        'cgpa_ranges': cgpa_ranges,
        'prob_ranges': prob_ranges,
        'avg_communication': round(avg_communication, 1),
        'avg_technical': round(avg_technical, 1),
        'avg_aptitude': round(avg_aptitude, 1),
        'total_students': StudentRecord.objects.count(),
        'total_predictions': predictions.count()
    }
    
    return render(request, 'predictor/placement/analytics.html', context)

# ==================== TRAINING SESSION MANAGEMENT ====================

@login_required
def manage_training_sessions(request):
    """List all training sessions"""
    sessions = TrainingSession.objects.all().order_by('-scheduled_date')
    
    # Filter by type
    session_type = request.GET.get('type')
    if session_type:
        sessions = sessions.filter(session_type=session_type)
    
    context = {
        'sessions': sessions,
        'session_types': TrainingSession.SESSION_TYPES
    }
    
    return render(request, 'predictor/placement/manage_sessions.html', context)

@login_required
def add_training_session(request):
    """Add new training session"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        session_type = request.POST.get('session_type')
        scheduled_date = request.POST.get('scheduled_date')
        scheduled_time = request.POST.get('scheduled_time')
        duration_minutes = request.POST.get('duration_minutes', 60)
        venue = request.POST.get('venue')
        max_students = request.POST.get('max_students', 50)
        resource_links = request.POST.get('resource_links', '')
        
        try:
            session = TrainingSession.objects.create(
                title=title,
                description=description,
                session_type=session_type,
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
                duration_minutes=duration_minutes,
                venue=venue,
                max_students=max_students,
                resource_links=resource_links,
                created_by=request.user
            )
            messages.success(request, f'Training session "{title}" created successfully!')
            return redirect('manage_training_sessions')
        except Exception as e:
            messages.error(request, f'Error creating session: {str(e)}')
    
    context = {
        'session_types': TrainingSession.SESSION_TYPES
    }
    
    return render(request, 'predictor/placement/add_session.html', context)

@login_required
def edit_training_session(request, session_id):
    """Edit training session"""
    session = get_object_or_404(TrainingSession, id=session_id)
    
    if request.method == 'POST':
        session.title = request.POST.get('title')
        session.description = request.POST.get('description')
        session.session_type = request.POST.get('session_type')
        session.scheduled_date = request.POST.get('scheduled_date')
        session.scheduled_time = request.POST.get('scheduled_time')
        session.duration_minutes = request.POST.get('duration_minutes')
        session.venue = request.POST.get('venue')
        session.max_students = request.POST.get('max_students')
        session.resource_links = request.POST.get('resource_links', '')
        session.is_active = request.POST.get('is_active') == 'on'
        
        try:
            session.save()
            messages.success(request, f'Training session "{session.title}" updated successfully!')
            return redirect('manage_training_sessions')
        except Exception as e:
            messages.error(request, f'Error updating session: {str(e)}')
    
    context = {
        'session': session,
        'session_types': TrainingSession.SESSION_TYPES
    }
    
    return render(request, 'predictor/placement/edit_session.html', context)

@login_required
def delete_training_session(request, session_id):
    """Delete training session"""
    session = get_object_or_404(TrainingSession, id=session_id)
    
    if request.method == 'POST':
        title = session.title
        session.delete()
        messages.success(request, f'Training session "{title}" deleted successfully!')
        return redirect('manage_training_sessions')
    
    context = {'session': session}
    return render(request, 'predictor/placement/delete_session_confirm.html', context)

@login_required
def placement_logout(request):
    """Logout"""
    logout(request)
    return redirect('placement_login')
