import logging
import pytest
import requests
import responses

from piedpiper.gman import client
from piedpiper.gman.exceptions import TaskError


@responses.activate
def test_debug(caplog):
    with caplog.at_level(logging.DEBUG):
        responses.add(
            responses.POST, "http://gman_url/task", json={"task": {"task_id": "1234"}}
        )

        client.request_new_task_id(
            "1234", "http://gman_url", "test", "tests", status="started"
        )
        assert "Requesting new taskID" in caplog.text


@responses.activate
def test_request_new_task_id():
    responses.add(
        responses.POST, "http://gman_url/task", json={"task": {"task_id": "1234"}}
    )

    resp = client.request_new_task_id(
        "1234", "http://gman_url", "test", "tests", status="started"
    )

    assert resp == {"task": {"task_id": "1234"}}


@responses.activate
def test_request_new_task_id_with_thread_id():
    responses.add(
        responses.POST, "http://gman_url/task", json={"task": {"task_id": "1234"}}
    )
    resp = client.request_new_task_id(
        "1234", "http://gman_url", "test", "tests", status="started", thread_id="1234"
    )
    assert resp == {"task": {"task_id": "1234"}}


def test_request_new_task_id_invalid_status(mock_post_request_exception):
    with pytest.raises(ValueError):
        client.request_new_task_id(
            "1234", "http://gman_url", "test", "tests", status="invalid"
        )


def test_request_new_task_id_no_status(mock_post_request_exception):
    with pytest.raises(ValueError):
        client.request_new_task_id("1234", "http://gman_url", "test", "tests")


def test_request_new_task_id_no_thread_id_with_received_status(
    mock_post_request_exception
):
    with pytest.raises(ValueError):
        client.request_new_task_id(
            "1234", "http://gman_url", "test", "tests", status="received"
        )


def test_request_new_task_id_exception(mock_post_request_exception):
    with pytest.raises(requests.exceptions.RequestException):
        client.request_new_task_id(
            "1234", "http://gman_url", "test", "tests", status="started"
        )


@pytest.mark.parametrize("response_code", [400, 500])
@responses.activate
def test_request_new_task_id_failure(response_code):
    responses.add(responses.POST, "http://gman_url/task", status=response_code)
    with pytest.raises(requests.exceptions.HTTPError):
        client.request_new_task_id(
            "1234", "http://gman_url", "test", "tests", status="started"
        )


@responses.activate
def test_wait_for_task_id(task_event_list):
    responses.add(
        responses.GET, "http://gman_url/task/1234/events", json=task_event_list
    )
    resp = client.wait_for_task_status(
        task_id="1234", status="completed", gman_url="http://gman_url"
    )

    assert resp


@pytest.mark.parametrize("response_code", [400, 500])
@responses.activate
def test_wait_for_task_id_fails_request(response_code):
    responses.add(
        responses.GET, "http://gman_url/task/1234/events", status=response_code
    )
    with pytest.raises(requests.exceptions.HTTPError):
        client.wait_for_task_status(
            task_id="1234", status="completed", gman_url="http://gman_url"
        )


def test_wait_for_task_id_request_exception(mock_get_request_exception):
    with pytest.raises(requests.exceptions.RequestException):
        client.wait_for_task_status(
            task_id="1234", status="running", gman_url="http://gman_url", retry_max=2
        )


@responses.activate
def test_wait_for_task_id_times_out(task_event_list):
    responses.add(
        responses.GET, "http://gman_url/task/1234/events", json=task_event_list
    )
    with pytest.raises(TimeoutError):
        client.wait_for_task_status(
            task_id="1234", status="running", gman_url="http://gman_url", retry_max=2
        )


@responses.activate
def test_wait_for_task_id_task_fails(task_event_list_failures):
    responses.add(
        responses.GET, "http://gman_url/task/1234/events", json=task_event_list_failures
    )
    with pytest.raises(TaskError):
        client.wait_for_task_status(
            task_id="1234", status="running", gman_url="http://gman_url", retry_max=2
        )


@responses.activate
def test_update_task_id():
    task_event = {
        "message": "blank message",
        "status": "running",
        "thread_id": "",
        "timestamp": "2019-05-16T19:56:33.231452+00:00",
        "task": {
            "project": "python_project",
            "run_id": "574b1db2-ae55-41bb-8680-43703f3031f2",
            "caller": "gateway",
            "task_id": "1234",
        },
    }
    responses.add(responses.PUT, "http://gman_url/task/1234", json=task_event)

    client.update_task_id(
        task_id="1234",
        status="running",
        message="blank message",
        gman_url="http://gman_url",
    )

    assert (
        responses.calls[0].request.body
        == '{"message": "blank message", "status": "running"}'
    )


@pytest.mark.parametrize("response_code", [400, 500])
@responses.activate
def test_update_task_id_fails_request(response_code):
    responses.add(responses.PUT, "http://gman_url/task/1234", status=response_code)
    with pytest.raises(requests.exceptions.HTTPError):
        client.update_task_id(
            task_id="1234",
            status="running",
            message="blank message",
            gman_url="http://gman_url",
        )


def test_update_task_id_request_exception(mock_put_request_exception):
    with pytest.raises(requests.exceptions.RequestException):
        client.update_task_id(
            task_id="1234",
            status="running",
            message="blank message",
            gman_url="http://gman_url",
        )


@responses.activate
def test_get_task_id_events(task_event_list):
    responses.add(
        responses.GET, "http://gman_url/task/1234/events", json=task_event_list
    )

    resp = client.get_task_id_events(task_id="1234", gman_url="http://gman_url")

    assert resp == task_event_list


@responses.activate
def test_get_task_id_events_query_filter_returns_none(task_event_list):
    responses.add(
        responses.GET, "http://gman_url/task/1234/events", json=task_event_list
    )
    resp = client.get_task_id_events(
        task_id="1234",
        gman_url="http://gman_url",
        query_filter=lambda x: x.get("status") == "delegated",
    )
    assert not len(resp)


@responses.activate
def test_get_task_id_events_returns_one_item(task_event_list):
    responses.add(
        responses.GET, "http://gman_url/task/1234/events", json=task_event_list
    )
    resp = client.get_task_id_events(
        task_id="1234",
        gman_url="http://gman_url",
        query_filter=lambda x: x.get("status") == "completed",
    )
    assert len(resp) == 1


@pytest.mark.parametrize("response_code", [400, 500])
@responses.activate
def test_get_task_id_events_fails_request(response_code):
    responses.add(
        responses.GET, "http://gman_url/task/1234/events", status=response_code
    )

    with pytest.raises(requests.exceptions.HTTPError):
        client.get_task_id_events(task_id="1234", gman_url="http://gman_url")


def test_get_task_id_events_request_exception(mock_get_request_exception):
    with pytest.raises(requests.exceptions.RequestException):
        client.get_task_id_events(task_id="1234", gman_url="http://gman_url")


@responses.activate
def test_get_thread_id_tasks(task_list):
    responses.add(responses.GET, "http://gman_url/thread/1234", json=task_list)
    resp = client.get_thread_id_tasks(thread_id="1234", gman_url="http://gman_url")
    assert len(resp)


@responses.activate
def test_get_thread_id_tasks_query_filter_returns_one(task_list):
    responses.add(responses.GET, "http://gman_url/thread/1234", json=task_list)
    resp = client.get_thread_id_tasks(
        thread_id="1234",
        gman_url="http://gman_url",
        query_filter=lambda x: x.get("caller") == "gateway",
    )
    assert len(resp) == 1


@pytest.mark.parametrize("response_code", [400, 500])
@responses.activate
def test_get_thread_id_tasks_fails_request(response_code):
    responses.add(responses.GET, "http://gman_url/thread/1234", status=response_code)
    with pytest.raises(requests.exceptions.HTTPError):
        client.get_thread_id_tasks(thread_id="1234", gman_url="http://gman_url")


def test_get_thread_id_tasks_request_exception(mock_get_request_exception):
    with pytest.raises(requests.exceptions.RequestException):
        client.get_thread_id_tasks(thread_id="1234", gman_url="http://gman_url")


@responses.activate
def test_get_thread_id_events(task_event_list):
    responses.add(
        responses.GET, "http://gman_url/thread/1234/events", json=task_event_list
    )
    resp = client.get_thread_id_events(thread_id="1234", gman_url="http://gman_url")
    assert resp


@responses.activate
def test_get_thread_id_events_returns_one_item(task_event_list):
    responses.add(
        responses.GET, "http://gman_url/thread/1234/events", json=task_event_list
    )
    resp = client.get_thread_id_events(
        thread_id="1234",
        gman_url="http://gman_url",
        query_filter=lambda x: x.get("status") == "completed",
    )
    assert len(resp) == 1


@pytest.mark.parametrize("response_code", [400, 500])
@responses.activate
def test_get_thread_id_events_fails_request(response_code):
    responses.add(
        responses.GET, "http://gman_url/thread/1234/events", status=response_code
    )
    with pytest.raises(requests.exceptions.HTTPError):
        client.get_thread_id_events(thread_id="1234", gman_url="http://gman_url")


def test_get_thread_id_events_request_exception(mock_get_request_exception):
    with pytest.raises(requests.exceptions.RequestException):
        client.get_thread_id_events(thread_id="1234", gman_url="http://gman_url")


@responses.activate
def test_wait_for_thread_id_complete():
    thread_status_headers = {
        "x-gman-tasks-running": "0",
        "x-gman-tasks-completed": "1",
        "x-gman-tasks-failed": "0",
    }

    responses.add(
        responses.HEAD, "http://gman_url/thread/1234", headers=thread_status_headers
    )
    resp = client.wait_for_thread_id_complete(
        thread_id="1234", gman_url="http://gman_url"
    )

    assert resp


@responses.activate
def test_wait_for_thread_id_complete_has_failures():
    thread_status_headers = {
        "x-gman-tasks-running": "0",
        "x-gman-tasks-completed": "1",
        "x-gman-tasks-failed": "1",
    }
    responses.add(
        responses.HEAD, "http://gman_url/thread/1234", headers=thread_status_headers
    )
    with pytest.raises(TaskError):
        client.wait_for_thread_id_complete(thread_id="1234", gman_url="http://gman_url")


@responses.activate
def test_wait_for_thread_id_complete_times_out():
    thread_status_headers = {
        "x-gman-tasks-running": "1",
        "x-gman-tasks-completed": "0",
        "x-gman-tasks-failed": "0",
    }
    responses.add(
        responses.HEAD, "http://gman_url/thread/1234", headers=thread_status_headers
    )
    with pytest.raises(TimeoutError):
        client.wait_for_thread_id_complete(
            thread_id="1234", gman_url="http://gman_url", retry_max=2
        )


@pytest.mark.parametrize("response_code", [400, 500])
@responses.activate
def test_wait_for_thread_id_complete_fails_request(response_code):
    responses.add(responses.HEAD, "http://gman_url/thread/1234", status=response_code)
    with pytest.raises(requests.exceptions.HTTPError):
        client.wait_for_thread_id_complete(thread_id="1234", gman_url="http://gman_url")


def test_wait_for_thread_id_complete_request_exception(mock_head_request_exception):
    with pytest.raises(requests.exceptions.RequestException):
        client.wait_for_thread_id_complete(thread_id="1234", gman_url="http://gman_url")
