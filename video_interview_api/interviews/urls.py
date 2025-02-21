from django.urls import path, include
from rest_framework.routers import DefaultRouter
from interviews.views import (
    add_interview, 
    add_position,
    PositionViewSet, 
    ApplicantViewSet, 
    QuestionViewSet, 
    ApplicantResponseViewSet, 
    InterviewViewSet,
    candidate_interviews,
    register,
    login_view,
    logout_view,
    review_interview,
    user_interviews,
    admin_dashboard,
    manage_interviews,
    manage_applicants,
    manage_positions,
    manage_questions,
    manage_responses,
    update_response_status,
    add_question,
    edit_question,
    delete_question,
    update_interview_status,
    edit_interview,
    delete_interview
)

# API Router Setup
router = DefaultRouter()
router.register(r'positions', PositionViewSet)
router.register(r'applicants', ApplicantViewSet)
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'applicant-responses', ApplicantResponseViewSet)
router.register(r'interviews', InterviewViewSet)

urlpatterns = [
    # API Endpoints
    path('api/', include(router.urls)),
    path('api/register/', register, name='register'),
    path('api/login/', login_view, name='login'),
    path('api/logout/', logout_view, name='logout'),
    path('api/user-interviews/', user_interviews, name='user_interviews'),

    # Admin Dashboard
    path('dashboard/', admin_dashboard, name='admin_dashboard'),

    # Positions Management
    path('positions/', manage_positions, name='manage_positions'),
    path('positions/add/', add_position, name='add_position'),

    # Questions Management
    path('questions/', manage_questions, name='manage_questions'),
    path('questions/add/', add_question, name='add_question'),
    path('questions/<int:question_id>/edit/', edit_question, name='edit_question'),
    path('questions/<int:question_id>/delete/', delete_question, name='delete_question'),

    # Applicants Management
    path('applicants/', manage_applicants, name='manage_applicants'),

    # Responses Management
    path('responses/', manage_responses, name='manage_responses'),
    path('responses/<int:response_id>/status/', update_response_status, name='update_response_status'),

    # Interviews Management
    path('interviews/', manage_interviews, name='manage_interviews'),
    path('interviews/add/', add_interview, name='add_interview'),
    path('interviews/<int:interview_id>/edit/', edit_interview, name='edit_interview'),
    path('interviews/<int:interview_id>/delete/', delete_interview, name='delete_interview'),
    path('interviews/<int:interview_id>/status/', update_interview_status, name='update_interview_status'),

    # Interview Review System
    path('candidates/', candidate_interviews, name='candidate_interviews'),
    path('interview/review/<int:interview_id>/', review_interview, name='review_interview'),
]