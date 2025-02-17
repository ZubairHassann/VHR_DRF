from rest_framework import viewsets, permissions
from .models import Applicant, Position, Question, ApplicantResponse
from .serializers import ApplicantSerializer, PositionSerializer, QuestionSerializer, ApplicantResponseSerializer
from rest_framework.parsers import MultiPartParser
from .models import Question
from .models import ApplicantResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from .serializers import ApplicantResponseSerializer  # Import your serializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets, permissions, serializers
from .models import Applicant, Position, Question, ApplicantResponse
from .serializers import ApplicantSerializer, PositionSerializer, QuestionSerializer, ApplicantResponseSerializer
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view


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

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [permissions.AllowAny]

class ApplicantViewSet(viewsets.ModelViewSet):
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        email = self.request.query_params.get('email')
        position_id = self.request.query_params.get('position')

        if email and position_id:
            queryset = queryset.filter(email=email, position_id=position_id) # Filter by both email and position ID
        elif email: # Optionally, filter just by email if you want to find all applicants with that email regardless of position
            queryset = queryset.filter(email=email)
        return queryset


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Question.objects.all()
        position_id_str = self.request.query_params.get('position', None) # Changed 'positions' to 'position'
        if position_id_str is not None:
            try:
                position_id = int(position_id_str)
                # Filter questions by position
                queryset = queryset.filter(positions__id=position_id)
            except ValueError:
                print(f"Invalid position ID: {position_id_str}")
                return Question.objects.none() # Return empty queryset if invalid ID
        return queryset


class ApplicantResponseViewSet(viewsets.ModelViewSet):
    queryset = ApplicantResponse.objects.all()
    serializer_class = ApplicantResponseSerializer
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser]