from rest_framework import serializers
from .models import Applicant, Position, Question, ApplicantResponse

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"

class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = "__all__"

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"



class ApplicantResponseSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all())
    class Meta:
        model = ApplicantResponse
        fields = ['applicant', 'question', 'video_response', 'submission_time', 'status']

    