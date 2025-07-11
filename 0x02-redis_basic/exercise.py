#!/usr/bin/env python3
"""
This module defines a Cache class for storing data in Redis using random keys.
"""

import redis
import uuid
from typing import Union


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
