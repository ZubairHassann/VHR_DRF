from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('video_interview/<int:applicant_id>/', views.video_interview, name='video_interview'),
]