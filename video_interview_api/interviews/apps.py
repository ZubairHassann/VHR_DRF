from django.apps import AppConfig

class InterviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interviews'

    def ready(self):
        # Import the template tags when the app is ready
        from video_interview_api.interviews.templatetags import response_filters