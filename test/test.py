def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


assert add(1, 2) == 3
assert add(-1, 1) == 0
assert add(0, 0) == 0

assert subtract(5, 3) == 2
assert subtract(0, 5) == -5
assert subtract(10, 10) == 0

print("모든 테스트 통과!")