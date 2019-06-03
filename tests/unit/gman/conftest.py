import pytest
import requests


@pytest.fixture
def task_list():
    tasks = [
        {
            "project": "python_project",
            "run_id": "574b1db2-ae55-41bb-8680-43703f3031f2",
            "caller": "gateway",
            "task_id": "1234",
            "thread_id": "1234",
        },
        {
            "project": "python_project",
            "run_id": "574b1db2-ae55-41bb-8680-43703f3031f2",
            "caller": "executor",
            "task_id": "1235",
            "thread_id": "1234",
        },
    ]

    return tasks


@pytest.fixture
def task_event_list():
    task_event_list = [
        {
            "task": {
                "project": "test",
                "task_id": "1234",
                "caller": "python",
                "thread_id": "1234",
                "run_id": "1234",
            },
            "timestamp": "2019-06-07T16:58:20.513731+00:00",
            "message": "Requesting new taskID",
            "status": "completed",
        },
        {
            "task": {
                "project": "test",
                "task_id": "1234",
                "caller": "python",
                "thread_id": "1234",
                "run_id": "1234",
            },
            "timestamp": "2019-06-07T16:58:34.177330+00:00",
            "message": "Requesting new taskID",
            "status": "received",
        },
    ]

    return task_event_list


@pytest.fixture
def task_event_list_failures():
    task_event_list_failures = [
        {
            "task": {
                "project": "test",
                "task_id": "1234",
                "caller": "python",
                "thread_id": "1234",
                "run_id": "1234",
            },
            "timestamp": "2019-06-07T16:58:20.513731+00:00",
            "message": "Requesting new taskID",
            "status": "completed",
        },
        {
            "task": {
                "project": "test",
                "task_id": "1234",
                "caller": "python",
                "thread_id": "1234",
                "run_id": "1234",
            },
            "timestamp": "2019-06-07T16:58:34.177330+00:00",
            "message": "Requesting new taskID",
            "status": "failed",
        },
    ]

    return task_event_list_failures


@pytest.fixture
def mock_get_request_exception(mocker):
    mocker.patch(
        "piedpiper.gman.client.requests.get", side_effect=requests.RequestException
    )


@pytest.fixture
def mock_head_request_exception(mocker):
    mocker.patch(
        "piedpiper.gman.client.requests.head", side_effect=requests.RequestException
    )


@pytest.fixture
def mock_post_request_exception(mocker):
    mocker.patch(
        "piedpiper.gman.client.requests.post", side_effect=requests.RequestException
    )


@pytest.fixture
def mock_put_request_exception(mocker):
    mocker.patch(
        "piedpiper.gman.client.requests.put", side_effect=requests.RequestException
    )
