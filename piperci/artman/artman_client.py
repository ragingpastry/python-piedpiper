import logging
import json
import requests

import piperci.gman.client as gman_client

log = logging.getLogger(__name__)


def _check_artifact_exists_for_sri(*, artman_url, sri_urlsafe):
    try:
        log.debug(f"Checking if artifact record exists for SRI {sri_urlsafe}")
        r = requests.head(f"{artman_url}/artifact/sri/{sri_urlsafe}")
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Unknown failure talking to artman. \n\n{e}"
        )
    if r.status_code == 404:
        log.debug(f"Artifact with SRI {sri_urlsafe} does not exist")
        return False
    elif r.status_code == 200:
        log.debug(f"Artifact with SRI {sri_urlsafe} exists")
        return True
    else:
        raise requests.exceptions.HTTPError(
            f"Unknown status code received from artman. {r.status_code} {r.text}"
        )


def _check_artifact_exists_for_task_id(*, artman_url, task_id):
    try:
        log.debug(f"Checking if artifact record exists for task_id {task_id}")
        r = requests.head(f"{artman_url}/artifact/task/{task_id}")
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Unknown failure talking to artman. \n\n{e}"
        )
    if r.status_code == 404:
        log.debug(f"Artifact with task_id {task_id} does not exists")
        return False
    elif r.status_code == 200:
        log.debug(f"Artifact with task_id {task_id} exists")
        return True
    else:
        raise requests.exceptions.HTTPError(
            f"Unknown status code received from artman. {r.status_code} {r.text}"
        )


def _get_artifact_by_artifact_id(*, artman_url, artifact_id):
    try:
        log.debug(f"Getting artifact records for artifact_id {artifact_id}")
        r = requests.get(f"{artman_url}/artifact/{artifact_id}")
        r.raise_for_status()
        log.debug(f"Received response from artman.\n{r.json}")
        return r.json()
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(
            f"Artifact not found with artifact_id {artifact_id}"
        ) from e
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"An unknown error occurred") from e


def _get_artifacts_by_sri(*, artman_url, sri_urlsafe, query_filter=None):
    try:
        log.debug(f"Getting artifact records for SRI {sri_urlsafe}")
        r = requests.get(f"{artman_url}/artifact/sri/{sri_urlsafe}")
        r.raise_for_status()
        log.debug(f"Received response from artman.\n{r.json}")
        if query_filter:
            return list(filter(query_filter, r.json()))
        else:
            return r.json()
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(
            f"Artifact not found with SRI {sri_urlsafe}"
        ) from e
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"An unknown error occurred") from e


def _get_artifacts_by_task_id(*, artman_url, task_id, query_filter=None):
    try:
        log.debug(f"Getting artifact records for task_id {task_id}")
        r = requests.get(f"{artman_url}/artifact/task/{task_id}")
        r.raise_for_status()
        log.debug(f"Received response from artman.\n{r.json}")
        if query_filter:
            return list(filter(query_filter, r.json()))
        else:
            return r.json()
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(
            f"Artifacts not found for task_id {task_id}"
        ) from e
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"An unknown error occurred") from e


def _get_artifacts_by_thread_id(
    *, artman_url, gman_url=None, thread_id, query_filter=None
):
    if not gman_url:
        gman_url = artman_url
    log.debug(f"Getting artifact records for thread_id {thread_id}")
    task_ids = [
        task.get("task_id")
        for task in gman_client.get_thread_id_tasks(
            thread_id=thread_id, gman_url=gman_url
        )
    ]
    artifacts = [
        artifact
        for task_id in task_ids
        for artifact in _get_artifacts_by_task_id(
            artman_url=artman_url, task_id=task_id
        )
    ]
    if query_filter:
        return list(filter(query_filter, artifacts))
    else:
        return artifacts


def check_artifact_exists(*, artman_url, sri_urlsafe=None, task_id=None):
    """
    Checks artman to see if an SRI has already been uploaded.
    :param artman_url: The artman endpoint as a string
    :param task_id: The task_id to query for as a string
    :param sri_urlsafe: the SRI hash to query for as a string. Must be URL-safe.
    :return: True if artifacts exist for the query, False if they don't.
    """
    mutually_exclusive_args = [arg for arg in [sri_urlsafe, task_id] if arg]
    if len(mutually_exclusive_args) > 1:
        raise ValueError(
            f"Multiple exclusive arguments given. You must pass exactly one of "
            f"sri_urlsafe and task_id."
        )
    if sri_urlsafe:
        return _check_artifact_exists_for_sri(
            artman_url=artman_url, sri_urlsafe=sri_urlsafe
        )
    elif task_id:
        return _check_artifact_exists_for_task_id(
            artman_url=artman_url, task_id=task_id
        )
    else:
        raise ValueError(
            f"One of sri_urlsafe, artifact_id, or task_id must be provided."
        )


def check_artifact_status(*, artman_url, artifact_id):
    """
    Checks the status of an artifact
    :param artman_url: Artman endpoint as a string
    :param artifact_id: Artifact ID to query for
    :return:
    """
    try:
        log.debug(f"Checking artifact status for artifact_id {artifact_id}")
        r = requests.head(f"{artman_url}/artifact/{artifact_id}")
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(
            f"Bad status code when querying artman"
        ) from e
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"An unknown error occurred when querying artifact status"
        ) from e
    return r.headers["x-gman-artifact-status"]


def get_artifact(
    *,
    artman_url,
    sri_urlsafe=None,
    artifact_id=None,
    task_id=None,
    thread_id=None,
    query_filter=None,
):
    """
    Gets metadata about an artifact. Only one of [sri_urlsafe, artifact_id, task_id]
    may be passed.
    :param artman_url: Artman endpoint as a string
    :param sri_urlsafe: URL-safe SRI of the artifact as a string
    :param artifact_id: ID of the artifact
    :param task_id: TaskID to query for
    :param thread_id: ThreadID to query for
    :param query_filter: A lambda expression to filter the results
    :return: List of artifact objects
    """
    mutually_exclusive_args = [
        arg for arg in [sri_urlsafe, artifact_id, task_id, thread_id] if arg
    ]
    if len(mutually_exclusive_args) > 1:
        raise ValueError(
            f"Multiple exclusive arguments given. You must pass exactly one of "
            f"sri_urlsafe, artifact_id, thread_id, and task_id."
        )

    if sri_urlsafe:
        return _get_artifacts_by_sri(
            artman_url=artman_url, sri_urlsafe=sri_urlsafe, query_filter=query_filter
        )
    elif artifact_id:
        return [
            _get_artifact_by_artifact_id(artman_url=artman_url, artifact_id=artifact_id)
        ]
    elif task_id:
        return _get_artifacts_by_task_id(
            artman_url=artman_url, task_id=task_id, query_filter=query_filter
        )
    elif thread_id:
        return _get_artifacts_by_thread_id(
            artman_url=artman_url, thread_id=thread_id, query_filter=query_filter
        )
    else:
        raise ValueError(
            f"One of sri_urlsafe, artifact_id, or task_id must be provided."
        )


def post_artifact(*, task_id, uri, type="artifact", caller, artman_url, sri):
    """
    Create a new artifact in ArtMan with the given parameters.
    :param task_id: The ID of the task to tie the artifact to.
    :param storage_uri: The URI that the artifact is located at
    :param type: The type. This is usually artifact.
    :param caller: The creator of the artifact record
    :param artman_url: The URL to reach artman
    :param sri: The SRI hash of the artifact
    :return: JSON response from ArtMan if the artifact doesn't exist. If the artifact
    does exist then we throw an exception.
    """
    try:
        log.debug(f"Creating new artifact record at {artman_url}")
        data = {
            "task_id": task_id,
            "caller": caller,
            "sri": sri,
            "uri": uri,
            "type": type,
        }
        r = requests.post(f"{artman_url}/artifact", data=json.dumps(data))
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Failed to create a new artifact record. \n\n{e}"
        )
    log.debug(f"Received from Artman: {r.json()}")
    return r.json()
