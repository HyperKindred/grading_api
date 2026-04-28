import math

def triangle_area(a: float, b: float, c: float) -> float:
    s = (a + b + c) / 2
    area = math.sqrt(s * (s - a) * (s - b) * (s - c))
    return area