#!/usr/bin/env python3
"""
This module defines a Cache class for storing data in Redis using random keys.
"""

import redis
import uuid
from typing import Union, Callable, Optional


class Cache:
    """
    Cache class for interacting with Redis key-value store.
    It stores data using a randomly generated key and supports multiple data types.
    """

    def __init__(self) -> None:
        """
        Initialize the Cache instance.
        Connects to Redis and clears the database using flushdb.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the provided data in Redis using a randomly generated UUID key.

        Args:
            data (Union[str, bytes, int, float]): The data to store in Redis.

        Returns:
            str: The randomly generated key used to store the data.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[bytes, str, int, float, None]:
        """
        Retrieve data from Redis and optionally convert it using fn.

        Args:
            key: The Redis key.
            fn: Optional function to apply to the data.

        Returns:
            The original data or the converted data.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve a string value from Redis.

        Args:
            key: The Redis key.

        Returns:
            The string representation or None.
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve an integer value from Redis.

        Args:
            key: The Redis key.

        Returns:
            The integer representation or None.
        """
        return self.get(key, fn=int)
