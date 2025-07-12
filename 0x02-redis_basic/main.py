#!/usr/bin/env python3
"""
Main file
"""

import redis
from exercise import Cache, replay

# Task 0: Store a value in Redis
cache = Cache()
data = b"hello"
key = cache.store(data)
print(key)

local_redis = redis.Redis()
print(local_redis.get(key))  # Should print: b'hello'

# Task 1: Test get with type recovery
TEST_CASES = {
    b"foo": None,
    123: int,
    "bar": lambda d: d.decode("utf-8")
}

for value, fn in TEST_CASES.items():
    key = cache.store(value)
    assert cache.get(key, fn=fn) == value

# Task 2: Count method calls
cache = Cache()
cache.store(b"first")
print(cache.get(cache.store.__qualname__))  # Should print: b'1'

cache.store(b"second")
cache.store(b"third")
print(cache.get(cache.store.__qualname__))  # Should print: b'3'

# Task 3: Log input/output history
s1 = cache.store("first")
print(s1)
s2 = cache.store("secont")
print(s2)
s3 = cache.store("third")
print(s3)

inputs = cache._redis.lrange(f"{cache.store.__qualname__}:inputs", 0, -1)
outputs = cache._redis.lrange(f"{cache.store.__qualname__}:outputs", 0, -1)

print("inputs: {}".format(inputs))
print("outputs: {}".format(outputs))

# Task 4: Replay the method call history
cache.store("foo")
cache.store("bar")
cache.store(42)
replay(cache.store)
