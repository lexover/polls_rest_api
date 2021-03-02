import json

import pytest

from django.urls import reverse

from rest_framework import status

from polls.models import Answer
from polls.serializers import AnswerSerializer

from .factories import QuestionsFactory
from .factories import AnswersFactory

base_url = 'answers'


# ===================== GET LIST ===================== #

@pytest.mark.django_db
def test_get_list_for_concrete_user(api_client, answer_fixture):
    expected = AnswerSerializer(answer_fixture[0]).data
    url = reverse(f'{base_url}-list')
    response = api_client.get(url, data={'user_id': expected.get('user_id')})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0] == expected


@pytest.mark.django_db
def test_get_list_without_user_empty(api_client, answer_fixture):
    url = reverse(f'{base_url}-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 0


@pytest.mark.django_db
def test_get_list_as_admin(api_client_as_admin, answer_fixture):
    expected = AnswerSerializer(answer_fixture, many=True).data
    url = reverse(f'{base_url}-list')
    response = api_client_as_admin.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected


# ===================== GET SINGLE ===================== #

@pytest.mark.django_db
def test_get_single_valid_as_admin(api_client_as_admin, answer_fixture):
    pk = answer_fixture[0].pk
    expected = AnswerSerializer(Answer.objects.get(pk=pk)).data
    url = reverse(f'{base_url}-detail', kwargs={'pk': pk})
    response = api_client_as_admin.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected


@pytest.mark.django_db
def test_get_single_valid_as_user(api_client, answer_fixture):
    pk = answer_fixture[1].pk
    user_id = answer_fixture[1].user_id
    expected = AnswerSerializer(Answer.objects.get(pk=pk)).data
    url = reverse(f'{base_url}-detail', kwargs={'pk': pk})
    response = api_client.get(url, data={'user_id': user_id})
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected


@pytest.mark.django_db
def test_get_single_invalid(api_client_as_admin, answer_fixture):
    response = api_client_as_admin.get(reverse(f'{base_url}-detail', kwargs={'pk': 99}))
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ===================== CREATE ===================== #

@pytest.mark.django_db
@pytest.mark.parametrize(
    'user_id, answer, type, status_code', [
        (1, 'Test_answer', 'TX', status.HTTP_201_CREATED),
        (1, '1', 'SO', status.HTTP_201_CREATED),
        (1, '1 2 3', 'MO', status.HTTP_201_CREATED),
        (1, 'Text', 'SO', status.HTTP_400_BAD_REQUEST),
        (1, '1 2 3', 'SO', status.HTTP_400_BAD_REQUEST),
        (1, 'Text', 'MO', status.HTTP_400_BAD_REQUEST),
        (1, '', 'TX', status.HTTP_400_BAD_REQUEST),
        (1, '', 'SO', status.HTTP_400_BAD_REQUEST),
        (1, '', 'MO', status.HTTP_400_BAD_REQUEST),
        (None, '', 'MO', status.HTTP_400_BAD_REQUEST)
    ]
)
def test_create(user_id, answer, type, status_code, api_client):
    question = QuestionsFactory.create(type=type)
    data = AnswersFactory.stub(user_id=user_id, question=question.pk, answer=answer)
    response = api_client.post(
        reverse(f'{base_url}-list'),
        data=json.dumps(data.__dict__),
        content_type='application/json'
    )
    assert response.status_code == status_code
    if response.status_code is status.HTTP_201_CREATED:
        assert response.data == {**data.__dict__, **{'id': response.data['id']}}


# ======================  UPDATE ==================== #

@pytest.mark.django_db
@ pytest.mark.parametrize(
    'user_id, text, type, status_code', [
        (0, 'Test_answer', 'TX', status.HTTP_200_OK),
        (0, '1', 'SO', status.HTTP_200_OK),
        (0, '1 2 3', 'MO', status.HTTP_200_OK),
        (0, 'Text', 'SO', status.HTTP_400_BAD_REQUEST),
        (0, '1 2 3', 'SO', status.HTTP_400_BAD_REQUEST),
        (0, 'Text', 'MO', status.HTTP_400_BAD_REQUEST),
        (0, '', 'TX', status.HTTP_400_BAD_REQUEST),
        (0, '', 'SO', status.HTTP_400_BAD_REQUEST),
        (0, '', 'MO', status.HTTP_400_BAD_REQUEST),
        (4, 'Test_answer', 'TX', status.HTTP_404_NOT_FOUND),
        (None, '', 'MO', status.HTTP_404_NOT_FOUND)
    ]
)
def test_update(user_id, text, type, status_code, api_client):
    question = QuestionsFactory.create(type=type)
    answer = AnswersFactory.create(question=question)
    if user_id != 0:
        answer.user_id = user_id
    answer.answer = text
    data = AnswerSerializer(answer).data
    response = api_client.put(
        reverse(f'{base_url}-detail', kwargs={'pk': answer.pk}),
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == status_code
    if status_code == status.HTTP_200_OK:
        assert AnswerSerializer(Answer.objects.get(pk=answer.pk)).data == data


# ======================  DELETE ==================== #

@pytest.mark.django_db
def test_delete_authorized(api_client_as_admin, answer_fixture):
    size_before = len(answer_fixture)
    removed_item = answer_fixture[0]
    url = reverse(f'{base_url}-detail', kwargs={'pk': removed_item.pk})
    response = api_client_as_admin.delete(url)
    size_after = Answer.objects.count()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert size_after == size_before - 1


@pytest.mark.django_db
def test_delete_unauthorized(api_client, answer_fixture):
    removed_item = answer_fixture[0]
    url = reverse(f'{base_url}-detail', kwargs={'pk': removed_item.pk})
    response = api_client.delete(url, data={'user_id': removed_item.user_id})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_delete_invalid(api_client_as_admin, answer_fixture):
    url = reverse(f'{base_url}-detail', kwargs={'pk': 99})
    response = api_client_as_admin.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
