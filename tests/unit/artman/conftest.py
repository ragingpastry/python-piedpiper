import pytest
import requests


@pytest.fixture
def artifacts():
    data = [
        {
            "uri": "https://someminio.example.com/art1",
            "sri": "sha256-sCDaaxdshXhK4sA/v4dMHiMWhtGyQwA1fP8PgrN0O5g=",
            "sri-urlsafe": "c2hhMjU2LXNDRGFheGRzaFhoSzRzQS92"
            "NGRNSGlNV2h0R3lRd0ExZlA4UGdyTjBPNWc9",
            "type": "artifact",
            "caller": "pytest",
        },
        {
            "uri": "https://someminio.example.com/art1",
            "sri": "sha256-sCDaaxdshXhK4sA/v4dMHiMWhtGyQwA1fP8PgrN0O5g=",
            "sri-urlsafe": "1234",
            "type": "artifact",
            "caller": "pytest",
        },
    ]

    return data


@pytest.fixture
def post_artifact_response():
    data = {
        "status": "unknown",
        "uri": "https://someminio.example.com/art1",
        "artifact_id": "884053a3-277b-45e4-9813-fc61c07a2cd6",
        "type": "artifact",
        "sri": "sha256-sCDaaxdshXhK4sA/v4dMHiMWhtGyQwA1fP8PgrN0O5g=",
        "task": {
            "task_id": "a9a1ca15-747d-43f9-8f04-1a66de8fef33",
            "caller": "test_case_create_1",
            "project": "gman_test_data",
            "thread_id": "a9a1ca15-747d-43f9-8f04-1a66de8fef33",
            "run_id": "create_1",
        },
        "event_id": "a48efe28-db9e-4330-93c4-5f480b2bef71",
    }

    return data


@pytest.fixture
def artifact_list(post_artifact_response):
    data = [post_artifact_response, post_artifact_response]
    return data


@pytest.fixture
def mock_post_request_exception(mocker):
    mocker.patch(
        "piperci.artman.artman_client.requests.post",
        side_effect=requests.RequestException,
    )


@pytest.fixture
def mock_head_request_exception(mocker):
    mocker.patch(
        "piperci.artman.artman_client.requests.head",
        side_effect=requests.RequestException,
    )


@pytest.fixture
def mock_get_request_exception(mocker):
    mocker.patch(
        "piperci.artman.artman_client.requests.get",
        side_effect=requests.RequestException,
    )


@pytest.fixture
def thread_id_tasks_fixture():
    tasks = [
        {
            "caller": "picli",
            "run_id": "f5209105-7666-49d3-9893-9f382e4b4a8d",
            "project": "python_project",
            "thread_id": "f147f4ba-742b-47d1-a24f-b3a4dad3830b",
            "task_id": "1234",
        }
    ]

    return tasks
