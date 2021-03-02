import factory
from datetime import datetime as dt
from datetime import timedelta as td
from polls.models import Poll
from polls.models import Question
from polls.models import Answer


class PollsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Poll

    title = factory.Sequence(lambda n: f'Poll_{n}')
    start_date = factory.Sequence(lambda n: (dt.now() + td(days=10) - td(days=n * 10)).strftime('%Y-%m-%d'))
    end_date = factory.Sequence(lambda n: (dt.now() + td(days=30) - td(days=n * 10)).strftime('%Y-%m-%d'))
    description = factory.Sequence(lambda n: f'Description_{n}')


class QuestionsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    text = factory.Faker('text')
    type = Question.TEXT
    poll = factory.SubFactory(PollsFactory)


class AnswersFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Answer

    user_id = factory.Sequence(lambda n: n)
    question = factory.SubFactory(QuestionsFactory)
    answer = factory.Sequence(lambda n: 'Answer_{n}')
