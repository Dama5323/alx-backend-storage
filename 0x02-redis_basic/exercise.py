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
    """Store the history of inputs and outputs for a function in Redis."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_data = str(args)
        method_name = method.__qualname__
        inputs_key = f"{method_name}:inputs"
        outputs_key = f"{method_name}:outputs"

        self._redis.rpush(inputs_key, input_data)
        result = method(self, *args, **kwargs)
        self._redis.rpush(outputs_key, result)

        return result
    return wrapper


def replay(method: Callable):
    """Display the history of calls of a particular function."""
    r = redis.Redis()
    method_name = method.__qualname__
    inputs_key = f"{method_name}:inputs"
    outputs_key = f"{method_name}:outputs"

    input_list = r.lrange(inputs_key, 0, -1)
    output_list = r.lrange(outputs_key, 0, -1)

    print(f"{method_name} was called {len(input_list)} times:")
    for inp, out in zip(input_list, output_list):
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
