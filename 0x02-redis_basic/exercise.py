#!/usr/bin/env python3
"""
This module defines a Cache class for storing and retrieving data from Redis.
It also includes decorators to count method calls, store call history, and replay them.
"""

import redis
import uuid
from functools import wraps
from typing import Union, Callable, Optional


def count_calls(method: Callable) -> Callable:
    """
    Decorator that counts how many times a method is called.
    Stores the count in Redis using the method's qualified name as key.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator that stores the history of inputs and outputs for a method.
    Inputs are stored in '<method_name>:inputs'
    Outputs are stored in '<method_name>:outputs'
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"
        self._redis.rpush(input_key, str(args))
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(output))
        return output
    return wrapper


def replay(method: Callable) -> None:
    """
    Display the history of calls of a particular function.
    It prints how many times the function was called,
    and the inputs and corresponding outputs for each call.
    """
    redis_instance = method.__self__._redis
    method_name = method.__qualname__
    call_count = int(redis_instance.get(method_name) or 0)

    print(f"{method_name} was called {call_count} times:")

    inputs = redis_instance.lrange(f"{method_name}:inputs", 0, -1)
    outputs = redis_instance.lrange(f"{method_name}:outputs", 0, -1)

    for inp, out in zip(inputs, outputs):
        print(f"{method_name}(*{inp.decode('utf-8')}) -> {out.decode('utf-8')}")


class Cache:
    """
    Cache class for interacting with Redis key-value store.
    Includes storing, retrieving, tracking usage, and replaying call history.
    """

    def __init__(self) -> None:
        """
        Initialize Redis connection and flush the database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store data in Redis under a randomly generated UUID key.

        Args:
            data: The data to store (str, bytes, int, float).

        Returns:
            The key under which the data was stored.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[bytes, str, int, float, None]:
        """
        Retrieve data from Redis and optionally apply a conversion function.

        Args:
            key: The Redis key.
            fn: Optional function to convert the data.

        Returns:
            The retrieved (and possibly converted) data, or None if key does not exist.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve a string value from Redis by decoding from bytes.

        Args:
            key: The Redis key.

        Returns:
            The decoded string, or None.
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve an integer value from Redis.

        Args:
            key: The Redis key.

        Returns:
            The integer representation, or None.
        """
        return self.get(key, fn=int)
