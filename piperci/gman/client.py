import json
import logging
import requests
import time

from piperci.gman.exceptions import TaskError

log = logging.getLogger(__name__)


def request_new_task_id(
    run_id=None, gman_url=None, project=None, caller=None, status=None, thread_id=None, parent_id=None
):
    """
    Request a new TaskID from GMan, associated with a given RunID
    :param run_id: Unique identifier to correlate taskIDs as a string
    :param gman_url: GMan endpoint as a string
    :param project: Name of your project as a string
    :param caller: The invoker of the task. as a string
    :param status: The initial status of the task. This must either be "started"
    or "received". Unless the caller of this function is an executor this should
    always be "started"
    :param: thread_id: The thread_id that this task should be associated with.
    This will mainly be used by executors who need to tie their task_id to the
    main task thread.
    :param: parent_id: The parent_id of the task which was delegated to this task.
    This is mainly used by executors who need to tie their task_id to the task
    of it's parent.
    :return: JSON resposne from GMan
    """
    if not status or (status != "started" and status != "received"):
        raise ValueError(f"Invalid status '{status}'. Must be 'received' or 'started'.")
    if status == "received" and (not thread_id or not parent_id):
        raise ValueError(f"thread_id must be specified if status is received.")
    try:
        log.debug(f"Requesting new taskID from gman at {gman_url}")
        data = {
            "run_id": run_id,
            "caller": caller,
            "project": project,
            "message": "Requesting new taskID",
            "status": status,
        }
        if thread_id:
            data.update({"thread_id": thread_id})
        if parent_id:
            data.update({"parent_id": parent_id})
        r = requests.post(f"{gman_url}/task", data=json.dumps(data))
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(
            f"GMan returned with a bad status code. \n\n{e}"
        )
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.HTTPError(
            f"Failed to request new task id from gman. \n\n{e}"
        )
    return r.json()


def wait_for_task_status(task_id=None, status=None, gman_url=None, retry_max=10):
    """
    Returns true if given task_id has a status of the given status. If retry_max
    is reached without a matching status then a Timeout exception is raised. If
    the given task returns with a "failed" state then we raise a TaskError exception.
    :param task_id: TaskID to query for as a string
    :param status: Status to wait for as a string
    :param gman_url: GMan endpoint as a string
    :param retry_max: The number of times to retry the query as an integer
    :return: True or exception
    """
    retries = 0
    while retries < retry_max:
        try:
            log.debug(f"Checking status of task {task_id}")
            r = requests.get(f"{gman_url}/task/{task_id}/events")
            r.raise_for_status()
            events = [event for event in r.json() if event.get("status") == status]
            events_failed = [
                event for event in r.json() if event.get("status") == "failed"
            ]
            if len(events_failed):
                raise TaskError(
                    f"Task {task_id} has failed task events. {events_failed}"
                )
            if len(events):
                return True
            else:
                retries += 1
                time.sleep(1)
        except requests.exceptions.HTTPError as e:
            raise requests.exceptions.HTTPError(
                f"GMan returned with a bad status code. \n\n{e}"
            )
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(
                f"Failed to check status of task. \n\n{e}"
            )

    raise TimeoutError(f"Checking task status timeout for task {task_id}")


def update_task_id(task_id=None, gman_url=None, status=None, message=None):
    """
    Updates a taskID status and/or message
    :param task_id: TaskID to update as a string
    :param gman_url: GMan endpoint as a string
    :param status: The status to apply to the task
    :param message: The message to apply to the task
    :return: JSON response from gman
    """
    try:
        data = {"message": message, "status": status}
        r = requests.put(f"{gman_url}/task/{task_id}", data=json.dumps(data))
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(
            f"GMan returned with a bad status code. \n\n{e}"
        )
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Failed to update taskID {task_id}. \n\n{e}"
        )
    return r.json()


def get_task_id_events(task_id=None, gman_url=None, query_filter=None):
    """
    Get a list of taskID events from gman.
    Optionally pass a query_fitler lamda expression to filter these events.
    For example, to return a list of all failed events for a particular taskID
    get_task_id_events(
      task_id='1234', gman_url=url, query_filter=lambda x: x.get('status') == 'failed'
    )
    :param task_id: taskID to query as a string
    :param gman_url: GMan endpoint as as string
    :param query_filter: lambda expression
    :return: List of events
    """
    try:
        r = requests.get(f"{gman_url}/task/{task_id}/events")
        r.raise_for_status()
        if query_filter:
            return list(filter(query_filter, r.json()))
        else:
            return r.json()
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(
            f"Gman returned with a bad status code. \n\n{e}"
        )
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Failed to get taskID events for task_id {task_id}. \n\n{e}"
        )


def get_thread_id_tasks(thread_id=None, gman_url=None, query_filter=None):
    """
    Get a list of tasks associated with the given thread_id
    :param thread_id: The thread_id to query with as a sring
    :param gman_url: The GMan endpoint as a string
    :param query_filter: lambda expression
    :return: List of tasks associated with thread_id
    """
    try:
        r = requests.get(f"{gman_url}/thread/{thread_id}")
        r.raise_for_status()
        if query_filter:
            return list(filter(query_filter, r.json()))
        else:
            return r.json()
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(
            f"Gman returned with a bad status code. \n\n{e}"
        )
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Failed to get tasks for thread_id {thread_id}. \n\n{e}"
        )


def get_thread_id_events(thread_id=None, gman_url=None, query_filter=None):
    """
    Get list of all events for a given thread_id, optionally filtered by
    a lambda expression.
    :param thread_id: Thread ID to query for as a string.
    :param gman_url:  GMan endpoint as a string.
    :param query_filter: Lambda expression
    :return: List of task events
    """
    try:
        r = requests.get(f"{gman_url}/thread/{thread_id}/events")
        r.raise_for_status()
        if query_filter:
            return list(filter(query_filter, r.json()))
        else:
            return r.json()
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(
            f"Gman returned with a bad status code. \n\n{e}"
        )
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Failed to get tasks for thread_id {thread_id}. \n\n{e}"
        )


def wait_for_thread_id_complete(thread_id=None, gman_url=None, retry_max=10):
    """
    Wait for all tasks under a given thread_id to return with a status of complete,
    up to the retry_max.
    :param thread_id: thread_id as a string to search for
    :param gman_url: GMan endpoint as a string
    :param retry_max: Number of times to retry as an integer
    :return: True or exception
    """
    retries = 0
    while retries < retry_max:
        try:
            log.debug(f"Checking status of thread {thread_id}")
            r = requests.head(f"{gman_url}/thread/{thread_id}")
            r.raise_for_status()
            running, completed, pending, failed = [
                r.headers.get(key)
                for key in [
                    "x-gman-tasks-running",
                    "x-gman-tasks-completed",
                    "x-gman-tasks-pending",
                    "x-gman-tasks-failed",
                ]
            ]
            if int(failed) > 0:
                raise TaskError(f"Thread {thread_id} has failures")
            elif int(running) > 0 or int(pending) > 0:
                retries += 1
                time.sleep(1)
            elif int(running) == 0 and int(completed) > 0 and int(pending) == 0:
                return True
            else:
                retries += 1
                time.sleep(1)
        except requests.exceptions.HTTPError as e:
            raise requests.exceptions.HTTPError(
                f"GMan returned with a bad status code. \n\n{e}"
            )
        except requests.exceptions.RequestException as e:
            raise requests.exceptions.RequestException(
                f"Failed to check status of task. \n\n{e}"
            )

    raise TimeoutError(f"Checking thread_id status timed out for thread_id {thread_id}")
