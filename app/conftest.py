import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient

from polls.tests.factories import PollsFactory
from polls.tests.factories import QuestionsFactory
from polls.tests.factories import AnswersFactory

register(PollsFactory)
register(QuestionsFactory)
register(AnswersFactory)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_client_as_admin(db, admin_user, api_client):
    api_client.force_authenticate(user=admin_user)
    yield api_client
    api_client.force_authenticate(user=None)


@pytest.fixture
def poll_fixture(db):
    return PollsFactory.create_batch(4)


@pytest.fixture
def question_fixture(db):
    return QuestionsFactory.create_batch(4)

@pytest.fixture
def answer_fixture(db):
    return AnswersFactory.create_batch(4)
