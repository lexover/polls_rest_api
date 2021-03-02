from django_filters import FilterSet
from polls.models import Question


class QuestionFilter(FilterSet):

    class Meta:
        model = Question
        fields = ['poll']
