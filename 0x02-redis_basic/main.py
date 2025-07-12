#!/usr/bin/env python3
"""
Main file
"""
import redis

Cache = __import__('exercise').Cache

# Initialize cache once
cache = Cache()

# Test basic store and retrieve
data = b"hello"
key = cache.store(data)
print(key)

local_redis = redis.Redis()
print(local_redis.get(key))  # Should print: b'hello'

# Test get with type recovery
TEST_CASES = {
    b"foo": None,
    123: int,
    "bar": lambda d: d.decode("utf-8")
}

for value, fn in TEST_CASES.items():
    key = cache.store(value)
    assert cache.get(key, fn=fn) == value
