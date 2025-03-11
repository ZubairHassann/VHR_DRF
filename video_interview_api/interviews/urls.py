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
    register,
    login_view,
    logout_view,
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
    delete_interview,
    ApplicantUpdateView,
    view_responses,
    manage_unique_applicants,
    view_applicant_responses,
    admin_login,
    admin_logout,
    update_response_status,
    send_email,
    send_applicant_email,
    add_job,
    PositionListCreateAPIView,
    ApplyJobAPIView
)

# API Router Setup
router = DefaultRouter()
router.register(r'positions', PositionViewSet)
router.register(r'applicants', ApplicantViewSet)
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'applicant-responses', ApplicantResponseViewSet)
router.register(r'interviews', InterviewViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', register, name='register'),
    path('api/login/', login_view, name='login'),
    path('api/logout/', logout_view, name='logout'),
    path('api/user-interviews/', user_interviews, name='user_interviews'),
    path('', admin_dashboard, name='admin_dashboard'),
    path('interviews/', manage_interviews, name='manage_interviews'),
    path('interviews/add/', add_interview, name='add_interview'),
    path('interviews/<int:interview_id>/edit/', edit_interview, name='edit_interview'),
    path('interviews/<int:interview_id>/delete/', delete_interview, name='delete_interview'),
    path('interviews/<int:interview_id>/status/', update_interview_status, name='update_interview_status'),

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
    path('applicants/<int:id>/', ApplicantUpdateView.as_view(), name='applicant_update'),
    path('api/applicant-responses/<int:pk>/status/', update_response_status, name='update_response_status'),

    # Responses Management
    path('responses/', manage_responses, name='manage_responses'),
    path('responses/<int:response_id>/status/', update_response_status, name='update_response_status'),
    path('view_responses/', view_responses, name='view_responses'),

    path('unique_applicants/', manage_unique_applicants, name='manage_unique_applicants'),
    path('unique_applicants/<str:email>/<int:position_id>/', view_applicant_responses, name='view_applicant_responses'),
    path('admin/login/', admin_login, name='admin_login'),
    path('admin/logout/', admin_logout, name='admin_logout'),
    path('responses/<int:response_id>/score/', update_response_status, name='update_response_score'),
    path('interviews/<int:interview_id>/send_email/', send_email, name='send_interview_email'),
    # path('interviews/<int:interview_id>/send_email/', send_interview_email, name='send_interview_email'),
    path('api/send_applicant_email/', send_applicant_email, name='send_applicant_email'),

    #Jobs
    path('api/positions/', PositionListCreateAPIView.as_view(), name='position_list_create'),
    path('api/positions/<int:position_id>/apply/', ApplyJobAPIView.as_view(), name='apply_job'),
    path('add-job/', add_job, name='add_job'),
]