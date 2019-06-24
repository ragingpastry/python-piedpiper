import pytest
import responses
import requests

from piperci.artman import artman_client

_post_artifact_data = {
    "artman_url": "http://artman_url",
    "uri": "https://someminio.example.com/art1",
    "sri": "sha256-sCDaaxdshXhK4sA/v4dMHiMWhtGyQwA1fP8PgrN0O5g=",
    "type": "artifact",
    "caller": "pytest",
    "task_id": "1234",
}


@responses.activate
def test_post_artifact(post_artifact_response):
    responses.add(
        responses.POST, "http://artman_url/artifact", json=post_artifact_response
    )

    results = artman_client.post_artifact(**_post_artifact_data)

    assert results == post_artifact_response


@pytest.mark.parametrize("response_code", [400, 500])
@responses.activate
def test_post_artifact_bad_response_code(response_code):
    responses.add(responses.POST, "http://artman_url/artifact", status=response_code)
    with pytest.raises(requests.exceptions.RequestException):
        artman_client.post_artifact(**_post_artifact_data)


def test_post_artifact_request_exception(mock_post_request_exception):
    with pytest.raises(requests.exceptions.RequestException):
        artman_client.post_artifact(**_post_artifact_data)


@pytest.mark.parametrize("test", [(200, True), (404, False)])
@responses.activate
def test_check_artifact_exists_for_sri_exists(test):
    responses.add(responses.HEAD, "http://artman_url/artifact/sri/1234", status=test[0])
    assert (
        artman_client._check_artifact_exists_for_sri(
            artman_url="http://artman_url", sri_urlsafe="1234"
        )
        == test[1]
    )


@responses.activate
def test_check_artifact_exists_for_sri_invalid_response():
    responses.add(responses.HEAD, "http://artman_url/artifact/sri/1234", status=400)
    with pytest.raises(requests.exceptions.RequestException):
        artman_client._check_artifact_exists_for_sri(
            artman_url="http://artman_url", sri_urlsafe="1234"
        )


def test_check_artifact_exists_for_sri_exception(mock_head_request_exception):
    with pytest.raises(requests.exceptions.RequestException):
        artman_client._check_artifact_exists_for_sri(
            artman_url="http://artman_url", sri_urlsafe="1234"
        )


@pytest.mark.parametrize("test", [(200, True), (404, False)])
@responses.activate
def test_check_artifact_exists_for_task_id_exists(test):
    responses.add(
        responses.HEAD, "http://artman_url/artifact/task/1234", status=test[0]
    )
    assert (
        artman_client._check_artifact_exists_for_task_id(
            artman_url="http://artman_url", task_id="1234"
        )
        == test[1]
    )


@responses.activate
def test_check_artifact_exists_for_task_id_invalid_response():
    responses.add(responses.HEAD, "http://artman_url/artifact/task/1234", status=400)
    with pytest.raises(requests.exceptions.RequestException):
        artman_client._check_artifact_exists_for_task_id(
            artman_url="http://artman_url", task_id="1234"
        )


def test_check_artifact_exists_for_task_id_exception(mock_head_request_exception):
    with pytest.raises(requests.exceptions.RequestException):
        artman_client._check_artifact_exists_for_task_id(
            artman_url="http://artman_url", task_id="1234"
        )


@pytest.mark.parametrize(
    "arg",
    [
        (
            {"artman_url": "http://artman_url", "task_id": "1234"},
            "task/1234",
            {"x-gman-artifacts": "2"},
        ),
        (
            {"artman_url": "http://artman_url", "sri_urlsafe": "1234"},
            "sri/1234",
            {"x-gman-artifacts": "2"},
        ),
    ],
)
@responses.activate
def test_check_artifact_exists(arg):
    responses.add(
        responses.HEAD, f"http://artman_url/artifact/{arg[1]}", headers=arg[2]
    )
    assert artman_client.check_artifact_exists(**arg[0])
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == f"http://artman_url/artifact/{arg[1]}"


@pytest.mark.parametrize(
    "arg",
    [
        {"artman_url": "http://artman_url", "task_id": "1234", "sri_urlsafe": "1234"},
        {"artman_url": "http://artman_url"},
    ],
)
@responses.activate
def test_check_artifact_exists_invalid_parameter(arg):
    with pytest.raises(ValueError):
        artman_client.check_artifact_exists(**arg)


@responses.activate
def test_check_artifact_status():
    responses.add(
        responses.HEAD,
        "http://artman_url/artifact/1234",
        headers={"x-gman-artifact-status": "unknown"},
    )
    response = artman_client.check_artifact_status(
        artman_url="http://artman_url", artifact_id="1234"
    )

    assert response == "unknown"


@pytest.mark.parametrize("response_code", [400, 500])
@responses.activate
def test_check_artifact_status_bad_response_code(response_code):
    responses.add(
        responses.HEAD, "http://artman_url/artifact/1234", status=response_code
    )
    with pytest.raises(requests.exceptions.HTTPError):
        artman_client.check_artifact_status(
            artman_url="http://artman_url", artifact_id="1234"
        )


def test_check_artifact_status_exception(mock_head_request_exception):
    with pytest.raises(requests.exceptions.RequestException):
        artman_client.check_artifact_status(
            artman_url="http://artman_url", artifact_id="1234"
        )


@responses.activate
def test_get_artifacts_by_sri(artifact_list):
    responses.add(
        responses.GET, "http://artman_url/artifact/sri/1234", json=artifact_list
    )

    response = artman_client._get_artifacts_by_sri(
        artman_url="http://artman_url", sri_urlsafe="1234"
    )

    assert len(response) == 2


@responses.activate
def test_get_artifacts_by_sri_query_filter(artifact_list):
    responses.add(
        responses.GET, "http://artman_url/artifact/sri/1234", json=artifact_list
    )
    response = artman_client._get_artifacts_by_sri(
        artman_url="http://artman_url",
        sri_urlsafe="1234",
        query_filter=lambda x: x.get("status") == "unknown",
    )
    assert len(response) == 2


@pytest.mark.parametrize("response_code", [400, 500])
@responses.activate
def test_get_artifacts_by_sri_bad_response_code(response_code):
    responses.add(
        responses.GET, "http://artman_url/artifact/sri/1234", status=response_code
    )
    with pytest.raises(requests.exceptions.HTTPError):
        artman_client._get_artifacts_by_sri(
            artman_url="http://artman_url", sri_urlsafe="1234"
        )


def test_get_artifacts_by_sri_request_exception(mock_get_request_exception):
    with pytest.raises(requests.exceptions.RequestException):
        artman_client._get_artifacts_by_sri(
            artman_url="http://artman_url", sri_urlsafe="1234"
        )


@responses.activate
def test_get_artifact_by_artifact_id(artifacts):
    responses.add(responses.GET, "http://artman_url/artifact/1234", json=artifacts[0])

    artman_client._get_artifact_by_artifact_id(
        artman_url="http://artman_url", artifact_id="1234"
    )

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "http://artman_url/artifact/1234"


@pytest.mark.parametrize("response_code", [400, 500])
@responses.activate
def test_get_artifact_by_artifact_id_bad_response_code(response_code):
    responses.add(
        responses.GET, "http://artman_url/artifact/1234", status=response_code
    )
    with pytest.raises(requests.exceptions.HTTPError):
        artman_client._get_artifact_by_artifact_id(
            artman_url="http://artman_url", artifact_id="1234"
        )


def test_get_artifact_by_artifact_id_request_exception(mock_get_request_exception):
    with pytest.raises(requests.exceptions.RequestException):
        artman_client._get_artifact_by_artifact_id(
            artman_url="http://artman_url", artifact_id="1234"
        )


@responses.activate
def test_get_artifact_by_task_id(artifacts):
    responses.add(responses.GET, "http://artman_url/artifact/task/1234", json=artifacts)
    artman_client._get_artifacts_by_task_id(
        artman_url="http://artman_url", task_id="1234"
    )
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "http://artman_url/artifact/task/1234"


@responses.activate
def test_get_artifacts_by_task_id_query_filter(artifact_list):
    responses.add(
        responses.GET, "http://artman_url/artifact/task/1234", json=artifact_list
    )
    response = artman_client._get_artifacts_by_task_id(
        artman_url="http://artman_url",
        task_id="1234",
        query_filter=lambda x: x.get("status") == "unknown",
    )
    assert len(response) == 2


@pytest.mark.parametrize("response_code", [400, 500])
@responses.activate
def test_get_artifacts_by_task_id_bad_response_code(response_code):
    responses.add(
        responses.GET, "http://artman_url/artifact/task/1234", status=response_code
    )
    with pytest.raises(requests.exceptions.HTTPError):
        artman_client._get_artifacts_by_task_id(
            artman_url="http://artman_url", task_id="1234"
        )


def test_get_artifacts_by_task_id_request_exception(mock_get_request_exception):
    with pytest.raises(requests.exceptions.RequestException):
        artman_client._get_artifacts_by_task_id(
            artman_url="http://artman_url", task_id="1234"
        )


@responses.activate
def test_get_artifact_by_thread_id(mocker, artifact_list, thread_id_tasks_fixture):
    responses.add(
        responses.GET, "http://artman_url/artifact/task/1234", json=artifact_list
    )
    mocker.patch(
        "piperci.gman.client.get_thread_id_tasks",
        return_value=thread_id_tasks_fixture,
    )
    artman_client._get_artifacts_by_thread_id(
        artman_url="http://artman_url", thread_id="1234"
    )
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "http://artman_url/artifact/task/1234"


@responses.activate
def test_get_artifacts_by_thread_id_query_filter(
    mocker, artifact_list, thread_id_tasks_fixture
):
    responses.add(
        responses.GET, "http://artman_url/artifact/task/1234", json=artifact_list
    )
    mocker.patch(
        "piperci.gman.client.get_thread_id_tasks",
        return_value=thread_id_tasks_fixture,
    )
    response = artman_client._get_artifacts_by_thread_id(
        artman_url="http://artman_url",
        thread_id="1234",
        query_filter=lambda x: x.get("status") == "unknown",
    )
    assert len(response) == 2


@pytest.mark.parametrize("response_code", [400, 500])
@responses.activate
def test_get_artifacts_by_thread_id_bad_response_code(
    mocker, response_code, thread_id_tasks_fixture
):
    responses.add(
        responses.GET, "http://artman_url/artifact/task/1234", status=response_code
    )
    mocker.patch(
        "piperci.gman.client.get_thread_id_tasks",
        return_value=thread_id_tasks_fixture,
    )
    with pytest.raises(requests.exceptions.HTTPError):
        artman_client._get_artifacts_by_thread_id(
            artman_url="http://artman_url", thread_id="1234"
        )


def test_get_artifacts_by_thread_id_request_exception(mock_get_request_exception):
    with pytest.raises(requests.exceptions.RequestException):
        artman_client._get_artifacts_by_thread_id(
            artman_url="http://artman_url", thread_id="1234"
        )


@pytest.mark.parametrize(
    "arg",
    [
        ({"artman_url": "http://artman_url", "task_id": "1234"}, "task/1234"),
        ({"artman_url": "http://artman_url", "sri_urlsafe": "1234"}, "sri/1234"),
        ({"artman_url": "http://artman_url", "artifact_id": "1234"}, "1234"),
    ],
)
@responses.activate
def test_get_artifact(arg, artifact_list):
    responses.add(
        responses.GET, f"http://artman_url/artifact/{arg[1]}", json=artifact_list
    )
    artman_client.get_artifact(**arg[0])
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == f"http://artman_url/artifact/{arg[1]}"


@responses.activate
def test_get_artifact_thread(mocker, artifact_list, thread_id_tasks_fixture):
    responses.add(
        responses.GET, "http://artman_url/artifact/task/1234", json=artifact_list
    )
    mocker.patch(
        "piperci.gman.client.get_thread_id_tasks",
        return_value=thread_id_tasks_fixture,
    )
    artman_client.get_artifact(
        artman_url="http://artman_url", thread_id="1234"
    )
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "http://artman_url/artifact/task/1234"


@pytest.mark.parametrize(
    "arg",
    [
        {"artman_url": "http://artman_url", "task_id": "1234", "sri_urlsafe": "1234"},
        {"artman_url": "http://artman_url", "thread_id": "1234", "sri_urlsafe": "1234"},
        {"artman_url": "http://artman_url", "thread_id": "1234", "task_id": "1234"},
        {
            "artman_url": "http://artman_url",
            "task_id": "1234",
            "sri_urlsafe": "1234",
            "artifact_id": "1234",
        },
        {
            "artman_url": "http://artman_url",
            "artifact_id": "1234",
            "sri_urlsafe": "1234",
            "thread_id": "1234"
        },
        {
            "artman_url": "http://artman_url",
            "artifact_id": "1234",
            "task_id": "1234",
            "thread_id": "1234"
        },
        {
            "artman_url": "http://artman_url",
            "sri_urlsafe": "1234",
            "task_id": "1234",
            "thread_id": "1234"
        },
        {"artman_url": "http://artman_url"},
    ],
)
@responses.activate
def test_get_artifact_invalid_parameter(arg):
    with pytest.raises(ValueError):
        artman_client.get_artifact(**arg)
