import contextlib

import agent.utils.consts


@contextlib.contextmanager
def retry_procedure(
    expected: list[type[Exception]] | None = None,
    ignored: list[type[Exception]] | None = None,
    max_retries: int = agent.utils.consts.DEFAULT_GENERAL_MAX_RETRIES
):
    """
    A context manager that allows for retrying a procedure in case of specified exceptions.

    Args:
        expected (list[type[Exception]] | None): A list of exception types that are expected to be raised during the procedure. Defaults to [Exception].
        ignored (list[type[Exception]] | None): A list of exception types that are ignored and do not trigger a retry. Defaults to an empty list.
        max_retries (int): The maximum number of retries. Defaults to the value of DEFAULT_GENERAL_MAX_RETRIES from agent.utils.consts.

    Yields:
        None: The context manager does not return any value.

    Raises:
        RuntimeError: If the procedure fails after reaching the maximum number of retries.

    Example:
        with retry_procedure(expected=[ConnectionError, TimeoutError], max_retries=3):
            # Code block to be retried in case of ConnectionError or TimeoutError
    """
    expected = expected or [Exception]  # Retry on ANY Exceptions
    ignored = ignored or []
    retry_counter = 0
    while True:
        try:
            yield
            break
        except tuple(expected) as failed_request:
            retry_counter += 1
            if retry_counter >= max_retries:
                raise RuntimeError(f'Failed after {retry_counter} retries') from failed_request
        except tuple(ignored):
            yield
            break
