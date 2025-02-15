from rest_framework import viewsets, permissions
from .models import Applicant, Position, Question, ApplicantResponse
from .serializers import ApplicantSerializer, PositionSerializer, QuestionSerializer, ApplicantResponseSerializer
from rest_framework.parsers import MultiPartParser
from .models import Question
from .models import ApplicantResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import ApplicantResponseSerializer  # Import your serializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes



@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def applicant_response_create(request):
    try:
        serializer = ApplicantResponseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True}, status=status.HTTP_201_CREATED)  # Only success key on success
        else:
            errors = serializer.errors
            print("Serializer errors:", errors)
            return Response({'success': False, 'error': errors}, status=status.HTTP_400_BAD_REQUEST)  # Include error key on failure
    except Exception as e:
        print("Exception:", e)
        return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  # Include error key on exception   

# @api_view(['POST'])
# def applicant_response_create(request):
#     serializer = ApplicantResponseSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     else:
#         print("Serializer errors:", serializer.errors)  # Print the errors
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [permissions.AllowAny]

class ApplicantViewSet(viewsets.ModelViewSet):
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    permission_classes = [permissions.AllowAny]

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.AllowAny]

class ApplicantResponseViewSet(viewsets.ModelViewSet):
    queryset = ApplicantResponse.objects.all()
    serializer_class = ApplicantResponseSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser] 
