from datetime import datetime, timedelta, timezone
import json
from django.db.models import Count, Q, Avg
from django.db.models.functions import ExtractMonth
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from rest_framework import generics, permissions, serializers, status, viewsets
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from .models import Applicant, ApplicantResponse, Interview, Position, Question
from .serializers import (
    ApplicantResponseSerializer,
    ApplicantSerializer,
    InterviewSerializer,
    PositionSerializer,
    QuestionSerializer,
)
from django.db.models import Count
from django.db import models 
from django.db.models import Count, Q 
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from django.db.models.functions import TruncMonth, ExtractMonth
import pandas as pd
from datetime import datetime, timedelta
from django.db.models import Count, Q, Avg, Sum
from django.db.models.functions import TruncDate, TruncMonth, ExtractMonth
from django.utils import timezone

@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not password or not email:
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password, email=email)
    return Response({'success': 'User registered successfully'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({'success': 'User logged in successfully'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'success': 'User logged out successfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def user_interviews(request):
    if not request.user.is_authenticated:
        return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

    applicants = Applicant.objects.filter(user=request.user)
    serializer = ApplicantSerializer(applicants, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@parser_classes([MultiPartParser])
def applicant_response_create(request):
    try:
        serializer = ApplicantResponseSerializer(data=request.data)
        if serializer.is_valid():
            response = serializer.save()
            if 'video_response' in request.FILES:
                response.video_response = request.FILES['video_response']
                response.save()
            return Response({'success': True}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# filepath: /home/reicho/Mega Sync Backups/Coding/VHR/VHR_DRF/video_interview_api/interviews/views.py
import logging

logger = logging.getLogger(__name__)

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [permissions.AllowAny]

    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.name = request.data.get('name', instance.name)  # Only update the name
            instance.is_active = request.data.get('is_active', instance.is_active)
            instance.save()
            return Response(PositionSerializer(instance).data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            logger.info(f"Deleting position {instance.id}")  # Add this line
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"Error deleting position: {str(e)}", exc_info=True)  # Add this line
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class ApplicantViewSet(viewsets.ModelViewSet):
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        email = self.request.query_params.get('email')
        position_id = self.request.query_params.get('position')

        if email and position_id:
            queryset = queryset.filter(email=email, position_id=position_id)
        elif email:
            queryset = queryset.filter(email=email)
        return queryset

class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Question.objects.all()
        position_id_str = self.request.query_params.get('position', None)
        if position_id_str is not None:
            try:
                position_id = int(position_id_str)
                queryset = queryset.filter(positions__id=position_id)
            except ValueError:
                return Question.objects.none()
        return queryset

class ApplicantResponseViewSet(viewsets.ModelViewSet):
    queryset = ApplicantResponse.objects.all()
    serializer_class = ApplicantResponseSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser]

class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    permission_classes = [permissions.AllowAny]


# @login_required
def manage_interviews(request):
    interviews = Interview.objects.all().order_by('-scheduled_date')
    return render(request, 'admin/manage_interviews.html', {
        'interviews': interviews
    })

# @login_required
@require_http_methods(["POST"])
def add_interview(request):
    try:
        title = request.POST.get('title')
        scheduled_date = request.POST.get('scheduled_date')
        description = request.POST.get('description', '')

        if title and scheduled_date:
            Interview.objects.create(
                title=title,
                scheduled_date=scheduled_date,
                description=description,
                status='pending'
            )
            # Return both status and message
            return JsonResponse({
                'status': 'success',
                'message': 'Interview scheduled successfully'
            })
        return JsonResponse({
            'status': 'error',
            'message': 'Missing required fields'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
    
# @login_required
@require_http_methods(["POST"])
def edit_interview(request, interview_id):
    try:
        interview = get_object_or_404(Interview, id=interview_id)
        interview.title = request.POST.get('title', interview.title)
        interview.scheduled_date = request.POST.get('scheduled_date', interview.scheduled_date)
        interview.description = request.POST.get('description', interview.description)
        interview.save()
        return JsonResponse({'message': 'Interview updated successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# @login_required
@require_http_methods(["DELETE"])
def delete_interview(request, interview_id):
    try:
        interview = get_object_or_404(Interview, id=interview_id)
        interview.delete()
        return JsonResponse({'message': 'Interview deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# @login_required
@require_http_methods(["POST"])
def update_interview_status(request, interview_id):
    try:
        interview = get_object_or_404(Interview, id=interview_id)
        status = request.POST.get('status')
        if status in ['pending', 'accepted', 'rejected']:
            interview.status = status
            interview.save()
            return JsonResponse({'message': f'Interview marked as {status}'})
        return JsonResponse({'error': 'Invalid status'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# @login_required
def manage_applicants(request):
    applicants = Applicant.objects.all().order_by('-id')
    return render(request, 'admin/manage_applicants.html', {'applicants': applicants})

# @login_required
@login_required
def manage_positions(request):
    positions = Position.objects.annotate(
        recent_applications=Count(
            'applicants',
            filter=Q(applicants__created_at__gte=timezone.now() - timedelta(days=7))
        )
    ).all()

    # Calculate statistics
    total_applicants = Applicant.objects.count()
    try:
        active_positions = positions.filter(is_active=True).count()
    except FieldError:
        # Fallback if is_active field doesn't exist yet
        active_positions = positions.count()
    
    fill_rate = (active_positions / positions.count() * 100) if positions.count() > 0 else 0
    active_positions = positions.filter(is_active=True).count()
    fill_rate = (active_positions / positions.count() * 100) if positions.count() > 0 else 0

    # Get trending position
    trending_position = positions.order_by('-recent_applications').first()

    # Prepare chart data
    positions_trend = Position.objects.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('-date')[:7]

    applicants_trend = Applicant.objects.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('-date')[:7]

    context = {
        'positions': positions,
        'total_applicants': total_applicants,
        'active_positions': active_positions,
        'fill_rate': round(fill_rate, 1),
        'trending_position': trending_position.name if trending_position else 'None',
        'trending_applications': trending_position.recent_applications if trending_position else 0,
        'positions_trend_labels': [p['date'].strftime('%b %d') for p in positions_trend],
        'positions_trend_data': [p['count'] for p in positions_trend],
        'applicants_trend_labels': [a['date'].strftime('%b %d') for a in applicants_trend],
        'applicants_trend_data': [a['count'] for a in applicants_trend],
    }

    return render(request, 'admin/manage_positions.html', context)

# @login_required
def manage_questions(request):
    questions = Question.objects.all().order_by('-id')
    return render(request, 'admin/manage_questions.html', {'questions': questions})


# @login_required
def add_position(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Position.objects.create(name=name)
            return redirect('manage_positions')
    return redirect('manage_positions')



# @login_required
def manage_questions(request):
    questions = Question.objects.all().prefetch_related('positions')
    positions = Position.objects.all()
    return render(request, 'admin/manage_questions.html', {
        'questions': questions,
        'positions': positions
    })

# @login_required
@require_http_methods(["POST"])
def add_question(request):
    text = request.POST.get('text')
    time_limit = request.POST.get('time_limit')
    position_ids = request.POST.getlist('positions')
    
    if text and time_limit and position_ids:
        question = Question.objects.create(
            text=text,
            time_limit=time_limit
        )
        question.positions.set(position_ids)
        messages.success(request, 'Question added successfully')
    else:
        messages.error(request, 'Please fill all required fields')
    
    return redirect('manage_questions')

# @login_required
@require_http_methods(["POST"])
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    text = request.POST.get('text')
    time_limit = request.POST.get('time_limit')
    position_ids = request.POST.getlist('positions')
    
    if text and time_limit and position_ids:
        question.text = text
        question.time_limit = time_limit
        question.save()
        question.positions.set(position_ids)
        messages.success(request, 'Question updated successfully')
    else:
        messages.error(request, 'Please fill all required fields')
    
    return redirect('manage_questions')

# @login_required
@require_http_methods(["DELETE"])
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    question.delete()
    return JsonResponse({'message': 'Question deleted successfully'})

# @login_required
def manage_responses(request):
    responses = ApplicantResponse.objects.all()
    
    # Filter by applicant if provided
    applicant_id = request.GET.get('applicant')
    if applicant_id:
        responses = responses.filter(applicant_id=applicant_id)
    
    responses = responses.select_related(
        'applicant', 'question', 'applicant__position'
    ).order_by('-submission_time')
    
    return render(request, 'admin/manage_responses.html', {
        'responses': responses,
        'applicant_id': applicant_id
    })

# @login_required
@csrf_exempt
@require_http_methods(["PATCH"])
def update_response_status(request, response_id):
    try:
        response = ApplicantResponse.objects.get(id=response_id)
        data = json.loads(request.body)
        score = data.get('score')
        if score is not None:
            response.score = score
        response.save()
        return JsonResponse({'message': 'Response updated successfully'}, status=200)
    except ApplicantResponse.DoesNotExist:
        return JsonResponse({'error': 'Response not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ApplicantUpdateView(View):
    def patch(self, request, id):
        try:
            applicant = Applicant.objects.get(id=id)
            data = json.loads(request.body)
            status = data.get('status')
            if status in ['Pending', 'Selected', 'Rejected']:
                applicant.status = status
                applicant.save()
                return JsonResponse({'message': 'Applicant status updated successfully'}, status=200)
            else:
                return JsonResponse({'error': 'Invalid status'}, status=400)
        except Applicant.DoesNotExist:
            return JsonResponse({'error': 'Applicant not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


def view_responses(request):
    applicant_id = request.GET.get('applicant')
    applicant = get_object_or_404(Applicant, id=applicant_id)
    responses = ApplicantResponse.objects.filter(applicant=applicant)
    return render(request, 'admin/view_responses.html', {'applicant': applicant, 'responses': responses})




# Add this view to list unique applicants
@login_required
def manage_unique_applicants(request):
    # Get base queryset with existing values and annotations
    unique_applicants = Applicant.objects.values(
        'id',
        'email', 
        'position',
        'position__name',
        'fullname',
        'status'
    ).annotate(
        responses_count=Count('responses')
    ).order_by('email')

    # Calculate statistics for stat cards
    total_count = unique_applicants.count()
    
    # Status counts
    status_counts = Applicant.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Initialize counts with default values
    selected_count = 0
    pending_count = 0
    rejected_count = 0
    
    # Update counts based on actual data
    for status in status_counts:
        if status['status'] == 'Selected':
            selected_count = status['count']
        elif status['status'] == 'Pending':
            pending_count = status['count']
        elif status['status'] == 'Rejected':
            rejected_count = status['count']

    # Calculate rates (prevent division by zero)
    selection_rate = round((selected_count / total_count * 100) if total_count > 0 else 0, 1)
    processing_rate = round((pending_count / total_count * 100) if total_count > 0 else 0, 1)
    rejection_rate = round((rejected_count / total_count * 100) if total_count > 0 else 0, 1)

    # Get application rate (applications in last 30 days compared to previous 30 days)
    today = timezone.now()
    thirty_days_ago = today - timedelta(days=30)
    sixty_days_ago = today - timedelta(days=60)
    
    recent_applications = Applicant.objects.filter(created_at__gte=thirty_days_ago).count()
    previous_applications = Applicant.objects.filter(
        created_at__gte=sixty_days_ago,
        created_at__lt=thirty_days_ago
    ).count()
    
    application_rate = round(
        ((recent_applications - previous_applications) / previous_applications * 100)
        if previous_applications > 0 else 0,
        1
    )

    context = {
        'unique_applicants': unique_applicants,
        'total_count': total_count,
        'selected_count': selected_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'selection_rate': selection_rate,
        'processing_rate': processing_rate,
        'rejection_rate': rejection_rate,
        'application_rate': application_rate
    }

    return render(request, 'admin/manage_unique_applicants.html', context)

# Add this view to show responses of a specific applicant
@login_required
def view_applicant_responses(request, email, position_id):
    applicant = get_object_or_404(Applicant, email=email, position_id=position_id)
    responses = ApplicantResponse.objects.filter(applicant=applicant)
    total_score = responses.aggregate(total=models.Sum('score'))['total'] or 0
    max_score = responses.count() * 10  # Assuming the max score for each response is 10
    total_questions = Question.objects.filter(positions=applicant.position).count()
    answered_questions = responses.count()
    return render(request, 'admin/view_applicant_responses.html', {
        'applicant': applicant,
        'responses': responses,
        'total_score': total_score,
        'max_score': max_score,
        'total_questions': total_questions,
        'answered_questions': answered_questions
    })

@login_required
def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            return render(request, 'admin/login.html', {
                'error': 'Invalid credentials or insufficient permissions'
            })
    
    return render(request, 'admin/login.html')



@login_required
@require_http_methods(["GET", "POST"])
def admin_logout(request):
    logout(request)
    return redirect('admin_login')




@login_required
def admin_dashboard(request):
    try:
        # Basic counts with safe completion rate calculation
        total_interviews = Interview.objects.count()
        completed_interviews = Interview.objects.filter(status='completed').count()
        completion_rate = round((completed_interviews / total_interviews * 100) if total_interviews > 0 else 0)

        # Calculate interview growth safely
        last_month = timezone.now() - timedelta(days=30)
        current_interviews = Interview.objects.filter(created_at__gte=last_month).count()
        previous_interviews = Interview.objects.filter(
            created_at__lt=last_month,
            created_at__gte=last_month - timedelta(days=30)
        ).count()
        interview_growth = round(
            ((current_interviews - previous_interviews) / previous_interviews * 100)
            if previous_interviews > 0 else 0
        )

        # Safe calculation of performance metrics
        total_applicants = Applicant.objects.count()
        total_positions = Position.objects.count()
        total_questions = Question.objects.count()
        total_responses = ApplicantResponse.objects.count()
        
        # Calculate performance metrics safely
        performance_metrics = [
            {
                'name': 'Selection Rate',
                'value': round((Applicant.objects.filter(status='Selected').count() / total_applicants * 100)
                             if total_applicants > 0 else 0),
                'trend': 5
            },
            {
                'name': 'Response Rate',
                'value': round((total_responses / (total_interviews * total_questions) * 100)
                             if (total_interviews * total_questions) > 0 else 0),
                'trend': -2
            },
            {
                'name': 'Position Fill Rate',
                'value': round((Position.objects.filter(applicants__status='Selected')
                              .distinct().count() / total_positions * 100)
                             if total_positions > 0 else 0),
                'trend': 3
            }
        ]

        # Get application trends for current year by month
        current_year = timezone.now().year
        application_trends = (
            Applicant.objects
            .filter(created_at__year=current_year)
            .annotate(
                month=ExtractMonth('created_at')
            )
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )

        # Format trend data
        trend_data = {
            'dates': [f"{current_year}-{str(entry['month']).zfill(2)}-01" for entry in application_trends],
            'counts': [entry['count'] for entry in application_trends]
        }

        # Get recent activities efficiently using prefetch_related
        recent_applications = (
            Applicant.objects
            .select_related('position')
            .order_by('-created_at')[:5]
        )

        recent_interviews = (
            Interview.objects
            .order_by('-created_at')[:5]
        )

        # Combine and sort activities
        recent_activities = []
        for app in recent_applications:
            recent_activities.append({
                'type': 'application',
                'description': f"{app.fullname} applied for {app.position.name}",
                'timestamp': app.created_at
            })
        
        for interview in recent_interviews:
            recent_activities.append({
                'type': 'interview',
                'description': f"New interview scheduled: {interview.title}",
                'timestamp': interview.created_at
            })
        
        recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)

        # Get status distribution
        status_distribution = (
            Applicant.objects
            .values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )

        # Get position statistics with applicant counts
        position_stats = (
            Position.objects
            .annotate(
                applicant_count=Count('applicants'),
                selected_count=Count('applicants', filter=Q(applicants__status='Selected')),
                rejected_count=Count('applicants', filter=Q(applicants__status='Rejected')),
                pending_count=Count('applicants', filter=Q(applicants__status='Pending'))
            )
            .order_by('name')
        )

        context = {
            'total_interviews': total_interviews,
            'completion_rate': completion_rate,
            'interview_growth': interview_growth,
            'interview_growth_abs': abs(interview_growth),
            'total_applicants': total_applicants,
            'total_positions': total_positions,
            'total_questions': total_questions,
            'total_responses': total_responses,
            'status_distribution': list(status_distribution),
            'position_stats': position_stats,
            'application_trends': trend_data,
            'performance_metrics': performance_metrics,
            'recent_activities': recent_activities[:10]
        }
        
        return render(request, 'admin/dashboard.html', context)

    except Exception as e:
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return render(request, 'admin/dashboard.html', {
            'error': 'Error loading dashboard data. Please try again.'
        })