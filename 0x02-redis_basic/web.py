#!/usr/bin/env python3
"""
Module that implements an expiring web cache and access counter.
"""

import redis
import requests
from typing import Callable
from functools import wraps

# Connect to local Redis server
_redis = redis.Redis()


def count_access(method: Callable) -> Callable:
    """
    Decorator to count how many times a URL is accessed.
    Stores count in Redis using key format 'count:{url}'.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        _redis.incr(f"count:{url}")
        return method(url)
    return wrapper


@count_access
def get_page(url: str) -> str:
    """
    Retrieve the HTML content of a given URL.
    Cache the result in Redis with a TTL of 10 seconds.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The HTML content of the page.
    """
    cached_key = f"cache:{url}"
    cached_content = _redis.get(cached_key)

    if cached_content:
        return cached_content.decode("utf-8")

    # Fetch content and cache it with 10s TTL
    response = requests.get(url)
    content = response.text
    _redis.setex(cached_key, 10, content)
    return content
