from django.urls import path, include
from rest_framework.routers import DefaultRouter
from interviews.views import PositionViewSet, ApplicantViewSet, QuestionViewSet, ApplicantResponseViewSet, register, login_view, logout_view, user_interviews

router = DefaultRouter()
router.register(r'positions', PositionViewSet)
router.register(r'applicants', ApplicantViewSet)
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'applicant-responses', ApplicantResponseViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/register/', register, name='register'),
    path('api/login/', login_view, name='login'),
    path('api/logout/', logout_view, name='logout'),
    path('api/user-interviews/', user_interviews, name='user_interviews'),
]