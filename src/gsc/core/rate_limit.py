from typing import Any
from functools import wraps
from math import floor
import time
import sys
import threading


def now():
    if hasattr(time, "monotonic"):
        return time.monotonic
    return time.time


class RateLimitException(Exception):
    def __init__(self, message, period_remaining):
        super().__init__(message)
        self.period_remaining = period_remaining or None


class RateLimitDecorator:
    def __init__(self, calls, period, callback_clock=now()) -> None:
        self.clamped_calls = max(1, min(sys.maxsize, floor(calls)))
        self.period = period
        self.callback_clock = callback_clock

        # Initialise the decorator state.
        self.last_reset = callback_clock()
        self.num_calls = 0

        # Add thread safety.
        self.lock = threading.RLock()

    def __call__(self, func) -> Any:
        @wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                try:
                    return self.__handle_function_call(func, *args, **kwargs)
                except RateLimitException as exception:
                    if exception.period_remaining is not None:
                        time.sleep(exception.period_remaining)
                    else:
                        raise exception

        return wrapper

    def __handle_function_call(self, func, *args, **kwargs):
        with self.lock:
            period_remaining = self.__period_remaining()

            # If the time window has elapsed then reset.
            if period_remaining <= 0:
                self.num_calls = 0
                self.last_reset = self.callback_clock()

            # Increase the number of attempts to call the function.
            self.num_calls += 1

            # If the number of attempts to call the function exceeds the
            # maximum then raise an exception.
            if self.num_calls > self.clamped_calls:
                raise RateLimitException("Too many calls", period_remaining)

        return func(*args, **kwargs)

    def __period_remaining(self):
        elapsed = self.callback_clock() - self.last_reset
        return self.period - elapsed


# pylint: disable=C0103
rate_limit = RateLimitDecorator
