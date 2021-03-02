from datetime import datetime as dt

from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import permissions
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .filters import QuestionFilter
from .models import Answer
from .models import Poll
from .models import Question
from .permissions import DeleteProhibition
from .permissions import ReadOnly
from .serializers import AnswerSerializer
from .serializers import PollSerializer
from .serializers import QuestionSerializer


class ApiRoot(APIView):
    """
    Base view
    """
    def get(self, request, format=None):
        return Response({
            'token_obtain_pair': reverse('token_obtain_pair', request=request, format=format),
            'token_refresh': reverse('token_refresh', request=request, format=format),
        })


class PollsViewSet(viewsets.ModelViewSet):
    """
    Returns a list of all *active* polls in the system.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser | ReadOnly]
    serializer_class = PollSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Poll.objects.all()
        else:
            return Poll.objects.filter(Q(start_date__lte=dt.now().date()) & Q(end_date__gte=dt.now().date()))

    def perform_update(self, serializer):
        start_date = self.request.data.get('start_date')
        if start_date is not None:
            exist_start = Poll.objects.get(pk=self.request.data.get('id')).start_date
            if dt.fromisoformat(start_date).date() != exist_start:
                raise serializers.ValidationError('Start date cannot be changed')


class QuestionsViewSet(viewsets.ModelViewSet):
    """
    Returns a list questions.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser | ReadOnly]

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = QuestionFilter


class AnswerViewSet(viewsets.ModelViewSet):
    """
    Returns an answers list for concrete user.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [DeleteProhibition | permissions.IsAdminUser]

    serializer_class = AnswerSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Answer.objects.all()
        else:
            user_id = self.request.query_params.get('user_id', self.request.data.get('user_id'))
            return Answer.objects.filter(user_id=user_id)
