from django.urls import path
from .views import index, video_interview

urlpatterns = [
    path("", index, name="index"),
    path("video-interview/<int:applicant_id>/", video_interview, name="video_interview"),
]
