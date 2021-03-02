import re

from rest_framework import serializers

from .models import Answer
from .models import Poll
from .models import Question


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'poll', 'text', 'type']


class PollSerializer(serializers.ModelSerializer):

    # Validate that start date lower then end date
    def validate(self, attrs):
        if attrs['start_date'] >= attrs['end_date']:
            raise serializers.ValidationError('Start date can`t be less then end')
        return attrs

    class Meta:
        model = Poll
        fields = ['id', 'title', 'start_date', 'end_date', 'description']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'user_id', 'question', 'answer']

    def validate(self, attrs):
        question_type = attrs['question'].type
        answer = attrs['answer']
        if question_type == Question.SINGLE_OPTION and not re.fullmatch(r'^\d$', answer):
            raise serializers.ValidationError(f'Answer for question with type `Single option` has to be a single digit')
        elif question_type == Question.MULTIPLE_OPTIONS and not re.fullmatch(r'^(\d{1}\s+)*\d{1}\s*$', answer):
            raise serializers.ValidationError(f'Answer for question with type `Multiple '
                                              f'option` be a digits separated by whitespace')
        return attrs
