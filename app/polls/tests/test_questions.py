import json

import pytest

from django.urls import reverse

from rest_framework import status

from polls.models import Question
from polls.serializers import QuestionSerializer

from .factories import QuestionsFactory
from .factories import PollsFactory

base_url = 'questions'
# ===================== GET LIST ===================== #

@pytest.mark.django_db
def test_get_list(api_client, question_fixture):
    expected = QuestionSerializer(Question.objects.all(), many=True).data
    url = reverse(f'{base_url}-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected


@pytest.mark.django_db
def test_get_list_by_poll(api_client, question_fixture):
    poll_pk = question_fixture[0].poll.pk
    expected = QuestionSerializer(Question.objects.filter(pk=poll_pk), many=True).data
    url = reverse(f'{base_url}-list')
    response = api_client.get(url, data={'poll': poll_pk})
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected


# ===================== GET SINGLE ===================== #

@pytest.mark.django_db
def test_get_single_valid(api_client, question_fixture):
    pk = question_fixture[0].pk
    expected = QuestionSerializer(Question.objects.get(pk=pk)).data
    url = reverse(f'{base_url}-detail', kwargs={'pk': pk})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected


@pytest.mark.django_db
def test_get_single_invalid(api_client_as_admin, question_fixture):
    url = reverse(f'{base_url}-detail', kwargs={'pk': 99})
    response = api_client_as_admin.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ===================== CREATE ===================== #

@pytest.mark.django_db
@pytest.mark.parametrize(
    'text, type, status', [
        ('Text_1', 'TX', status.HTTP_201_CREATED),
        ('Text_1', 'SO', status.HTTP_201_CREATED),
        ('Text_1', 'MO', status.HTTP_201_CREATED),
        ('', 'TX', status.HTTP_400_BAD_REQUEST),
        ('Text_1', 'ER', status.HTTP_400_BAD_REQUEST),
        ('Text_1', '', status.HTTP_400_BAD_REQUEST),
    ]
)
def test_create_authorized(text, type, status, api_client_as_admin):
    poll = PollsFactory.create()
    question = {**QuestionsFactory.stub(text=text, type=type).__dict__, **{'poll': poll.pk}}
    response = api_client_as_admin.post(
        reverse(f'{base_url}-list'),
        data=json.dumps(question),
        content_type='application/json'
    )
    assert response.status_code == status


@pytest.mark.django_db
def test_create_unauthorized(api_client):
    poll = PollsFactory.create()
    question = {**QuestionsFactory.stub(text='T', type='TX').__dict__, **{'poll': poll.pk}}
    response = api_client.post(
        reverse(f'{base_url}-list'),
        data=json.dumps(question),
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ===================== UPDATE ===================== #

@pytest.mark.django_db
@pytest.mark.parametrize(
    'text, type, status_code', [
        ('Text_1', 'TX', status.HTTP_200_OK),
        ('', 'TX', status.HTTP_400_BAD_REQUEST),
        ('Text_1', 'ER', status.HTTP_400_BAD_REQUEST),
    ]
)
def test_update_authorized(text, type, status_code, api_client_as_admin):
    question = QuestionsFactory.create()
    question.text = text
    question.type = type
    data = QuestionSerializer(question).data
    response = api_client_as_admin.put(
        reverse(f'{base_url}-detail', kwargs={'pk': question.pk}),
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert QuestionSerializer(Question.objects.get(pk=question.pk)).data == data

@pytest.mark.django_db
def test_unauthorized_update_question(api_client):
    question = QuestionsFactory.create()
    question_data = QuestionSerializer(question).data
    response = api_client.put(
        reverse(f'{base_url}-detail', kwargs={'pk': question.pk}),
        data=json.dumps(question_data),
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ======================  DELETE ==================== #

@pytest.mark.django_db
def test_delete_authorized(api_client_as_admin, question_fixture):
    size_before = len(question_fixture)
    removed_item = question_fixture[0]
    url = reverse(f'{base_url}-detail', kwargs={'pk': removed_item.pk})
    response = api_client_as_admin.delete(url)
    size_after = Question.objects.count()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert size_after == size_before - 1


@pytest.mark.django_db
def test_delete_unauthorized(api_client, question_fixture):
    removed_item = question_fixture[0]
    url = reverse(f'{base_url}-detail', kwargs={'pk': removed_item.pk})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_delete_invalid(api_client_as_admin, question_fixture):
    url = reverse(f'{base_url}-detail', kwargs={'pk': 99})
    response = api_client_as_admin.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
