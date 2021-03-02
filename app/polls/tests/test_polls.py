import json
from datetime import datetime as dt

import pytest

from django.db.models import Q
from django.urls import reverse

from rest_framework import status

from polls.models import Poll
from polls.serializers import PollSerializer

from .factories import PollsFactory


base_url = 'polls'
# ===================== GET LIST ===================== #

@pytest.mark.django_db
def test_get_list_unauthorized(api_client, poll_fixture):
    polls = Poll.objects.filter(Q(start_date__lte=dt.now().date())
                                & Q(end_date__gte=dt.now().date()))
    expected = PollSerializer(polls, many=True).data
    url = reverse(f'{base_url}-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected


@pytest.mark.django_db
def test_get_list_as_admin(api_client_as_admin, poll_fixture):
    expected = PollSerializer(Poll.objects.all(), many=True).data
    url = reverse(f'{base_url}-list')
    response = api_client_as_admin.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected

# ===================== GET SINGLE ===================== #


@pytest.mark.django_db
def test_get_single_valid_as_admin(api_client_as_admin, poll_fixture):
    pk = poll_fixture[0].pk
    expected = PollSerializer(Poll.objects.get(pk=pk)).data
    url = reverse(f'{base_url}-detail', kwargs={'pk': pk})
    response = api_client_as_admin.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == expected


@pytest.mark.django_db
def test_get_single_invalid(api_client_as_admin, poll_fixture):
    response = api_client_as_admin.get(reverse(f'{base_url}-detail', kwargs={'pk': 99}))
    assert response.status_code == status.HTTP_404_NOT_FOUND


# ===================== CREATE ===================== #

@pytest.mark.django_db
@pytest.mark.parametrize(
    'title, start, end, descr, status_code', [
        ('Poll', '2020-01-01', '2020-02-01', 'Descr', status.HTTP_201_CREATED),
        ('Poll', '2020-01-01', '2020-02-01', '', status.HTTP_201_CREATED),
        ('', '2020-01-01', '2020-02-01', 'Descr', status.HTTP_400_BAD_REQUEST),
        ('Poll', '2020-02-01', '2020-01-01', 'Descr', status.HTTP_400_BAD_REQUEST),
    ]
)
def test_create_authorized(title, start, end, descr, status_code, api_client_as_admin):
    data = PollsFactory.stub(title=title, start_date=start, end_date=end, description=descr)
    response = api_client_as_admin.post(
        reverse(f'{base_url}-list'),
        data=json.dumps(data.__dict__),
        content_type='application/json'
    )
    assert response.status_code == status_code
    if response.status_code is status.HTTP_201_CREATED:
        assert response.data == {**data.__dict__, **{'id': response.data['id']}}

@pytest.mark.django_db
def test_create_unauthorized(api_client):
    data = PollsFactory.stub(title='Poll', start_date='2020-01-01', end_date='2020-02-01', description='')
    response = api_client.post(
        reverse(f'{base_url}-list'),
        data=json.dumps(data.__dict__),
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ======================  UPDATE ==================== #

@pytest.mark.django_db
@pytest.mark.parametrize(
    'title, start_date, end_date, description, status_code', [
        ('Poll', '2020-01-01', '2020-02-01', 'Descr', status.HTTP_200_OK),
        ('Poll', '2020-01-01', '2020-02-01', '', status.HTTP_200_OK),
        ('', '2020-01-01', '2020-02-01', 'Descr', status.HTTP_400_BAD_REQUEST),
        ('Poll', '2020-02-01', '2020-01-01', 'Descr', status.HTTP_400_BAD_REQUEST),
        ('Poll', '2020-01-03', '2020-02-01', 'Descr', status.HTTP_400_BAD_REQUEST),
    ]
)
def test_update_authorized(title, start_date, end_date, description, status_code, api_client_as_admin):
    # We can't use polls_fixture here, because start_date have to be lower then end_date and same as in parameter
    poll = PollsFactory.create(title='TestPoll', start_date='2020-01-01', end_date='2020-02-01', description='')
    poll.title = title
    poll.start_date = start_date
    poll.end_date = end_date
    poll.description = description
    data = PollSerializer(poll).data
    response = api_client_as_admin.put(
        reverse(f'{base_url}-detail', kwargs={'pk': poll.pk}),
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == status_code


@pytest.mark.django_db
def test_unauthorized_update_poll(api_client):
    poll = PollsFactory.create(title='Poll', start_date='2020-01-01', end_date='2020-02-01', description='')
    poll.title = 'Poll_1'
    data = PollSerializer(poll).data
    response = api_client.put(
        reverse(f'{base_url}-detail', kwargs={'pk': poll.pk}),
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ======================  DELETE ==================== #

@pytest.mark.django_db
def test_valid_delete_poll(api_client_as_admin, poll_fixture):
    size_before = len(poll_fixture)
    removed_item = poll_fixture[0]
    url = reverse(f'{base_url}-detail', kwargs={'pk': removed_item.pk})
    response = api_client_as_admin.delete(url)
    size_after = Poll.objects.count()
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert size_after == size_before - 1

@pytest.mark.django_db
def test_unauthorized_delete_poll(api_client, poll_fixture):
    removed_item = poll_fixture[0]
    url = reverse(f'{base_url}-detail', kwargs={'pk': removed_item.pk})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
def test_invalid_delete_poll(api_client_as_admin, poll_fixture):
    url = reverse(f'{base_url}-detail', kwargs={'pk': 99})
    response = api_client_as_admin.delete(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
