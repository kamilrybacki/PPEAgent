import contextlib

import agent.utils.config


@contextlib.contextmanager
def retry_procedure(
  expected: list[type[Exception]] | None = None,
  ignored: list[type[Exception]] | None = None,
  max_retries: int = agent.utils.config.GENERAL_MAX_RETRIES
):
    expected = expected or [Exception]
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
