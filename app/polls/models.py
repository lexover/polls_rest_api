from django.db import models


class Poll(models.Model):
    title = models.CharField(max_length=120, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        return f'Poll #{self.pk} {self.title} start: {self.start_date} ' \
               f'end: {self.end_date}; description: {self.description}'


class Question(models.Model):
    TEXT = 'TX'
    SINGLE_OPTION = 'SO'
    MULTIPLE_OPTIONS = 'MO'

    QUESTION_TYPE_CHOICES = [
        (TEXT, 'Text answer'),
        (SINGLE_OPTION, 'Select single option'),
        (MULTIPLE_OPTIONS, 'Select several of the options')
    ]

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(blank=False)
    type = models.CharField(max_length=2, choices=QUESTION_TYPE_CHOICES)

    def __str__(self):
        return f'Question #{self.pk} for poll: "{self.poll}" text: "{self.text}", type: {self.type}'


class Answer(models.Model):

    user_id = models.BigIntegerField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    answer = models.TextField()

    def __str__(self):
        return f'Answer #{self.pk} for question "{self.question}" by user "{self.user_id}": {self.answer}'
