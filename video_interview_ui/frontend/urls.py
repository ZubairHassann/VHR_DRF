from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('video_interview/<int:applicant_id>/', views.video_interview, name='video_interview'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('interviews/', views.interviews, name='interviews'),
]