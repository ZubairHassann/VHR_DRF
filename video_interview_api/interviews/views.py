from datetime import datetime
import json

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

# @api_view(['POST'])
# @parser_classes([MultiPartParser])
# def applicant_response_create(request):
#     try:
#         serializer = ApplicantResponseSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'success': True}, status=status.HTTP_201_CREATED)
#         else:
#             errors = serializer.errors
#             return Response({'success': False, 'error': errors}, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    
class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [permissions.AllowAny]

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
def admin_dashboard(request):
    context = {
        'total_interviews': Interview.objects.count(),
        'total_applicants': Applicant.objects.count(),
        'total_positions': Position.objects.count(),
        'total_questions': Question.objects.count(),
    }
    return render(request, 'admin/dashboard.html', context)

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
            return JsonResponse({'message': 'Interview scheduled successfully'})
        return JsonResponse({'error': 'Missing required fields'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

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
def manage_positions(request):
    # if not request.user.is_staff:
    #     return redirect('login')
    positions = Position.objects.all().order_by('name')
    return render(request, 'admin/manage_positions.html', {'positions': positions})

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
@require_http_methods(["PATCH"])
def update_response_status(request, response_id):
    response = get_object_or_404(ApplicantResponse, id=response_id)
    status = request.POST.get('status')
    
    if status in ['Pending', 'Accepted', 'Rejected']:
        response.status = status
        response.save()
        
        # Update applicant status if needed
        if status == 'Rejected':
            response.applicant.status = 'Rejected'
            response.applicant.save()
        elif status == 'Accepted' and all(r.status == 'Accepted' for r in response.applicant.responses.all()):
            response.applicant.status = 'Selected'
            response.applicant.save()
            
        return JsonResponse({'message': f'Response marked as {status}'})
    
    return JsonResponse({'error': 'Invalid status'}, status=400)


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