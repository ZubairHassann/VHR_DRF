from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from interviews.views import PositionViewSet, ApplicantViewSet, QuestionViewSet, ApplicantResponseViewSet

router = DefaultRouter()
router.register(r'positions', PositionViewSet)
router.register(r'applicants', ApplicantViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'applicant-responses', ApplicantResponseViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
