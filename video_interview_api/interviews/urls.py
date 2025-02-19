from django.urls import path, include
from rest_framework.routers import DefaultRouter
from interviews.views import add_position,PositionViewSet, ApplicantViewSet, QuestionViewSet, ApplicantResponseViewSet, InterviewViewSet, register, login_view, logout_view, user_interviews, admin_dashboard, manage_interviews, manage_applicants, manage_positions, manage_questions, manage_responses, update_response_status, add_question, edit_question, delete_question

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
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('interviews/', manage_interviews, name='manage_interviews'),
    path('applicants/', manage_applicants, name='manage_applicants'),
    path('positions/', manage_positions, name='manage_positions'),
    path('questions/', manage_questions, name='manage_questions'),
    path('questions/add/', add_question, name='add_question'),
    path('questions/<int:question_id>/edit/', edit_question, name='edit_question'),
    path('questions/<int:question_id>/delete/', delete_question, name='delete_question'),
    path('responses/', manage_responses, name='manage_responses'),
    path('responses/<int:response_id>/status/', update_response_status, name='update_response_status'),
    path('add-position/', add_position, name='add_position'),
]