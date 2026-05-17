from __future__ import annotations

import math


class Vec2:
    __slots__ = ("_x", "_y")

    def __init__(self, x: float, y: float):
        self._x = float(x)
        self._y = float(y)

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    def __repr__(self):
        return f"Vec2({self._x}, {self._y})"

    def __eq__(self, other):
        if not isinstance(other, Vec2):
            return NotImplemented
        return self._x == other._x and self._y == other._y

    def __hash__(self):
        return hash((self._x, self._y))

    def __add__(self, other: Vec2) -> Vec2:
        return Vec2(self._x + other._x, self._y + other._y)

    def __sub__(self, other: Vec2) -> Vec2:
        return Vec2(self._x - other._x, self._y - other._y)

    def __mul__(self, scalar: float) -> Vec2:
        return Vec2(self._x * scalar, self._y * scalar)

    def __rmul__(self, scalar: float) -> Vec2:
        return Vec2(self._x * scalar, self._y * scalar)

    def __neg__(self) -> Vec2:
        return Vec2(-self._x, -self._y)

    def dot(self, other: Vec2) -> float:
        return self._x * other._x + self._y * other._y

    def cross(self, other: Vec2) -> float:
        return self._x * other._y - self._y * other._x

    def length(self) -> float:
        return math.sqrt(self._x * self._x + self._y * self._y)

    def length_sq(self) -> float:
        return self._x * self._x + self._y * self._y

    def normalized(self) -> Vec2:
        l = self.length()
        if l == 0:
            return Vec2(0, 0)
        return Vec2(self._x / l, self._y / l)

    def tuple(self) -> tuple[float, float]:
        return (self._x, self._y)


def cross3(o: Vec2, a: Vec2, b: Vec2) -> float:
    return (a - o).cross(b - o)


def orientation(o: Vec2, a: Vec2, b: Vec2) -> int:
    c = cross3(o, a, b)
    if c > 0:
        return 1
    if c < 0:
        return -1
    return 0


def is_convex(prev: Vec2, curr: Vec2, succ: Vec2) -> bool:
    return orientation(prev, curr, succ) > 0


def polygon_area_signed(vertices: list[Vec2]) -> float:
    n = len(vertices)
    if n < 3:
        return 0.0
    total = 0.0
    for i in range(n):
        j = (i + 1) % n
        total += vertices[i].x * vertices[j].y
        total -= vertices[j].x * vertices[i].y
    return total / 2.0


def polygon_area(vertices: list[Vec2]) -> float:
    return abs(polygon_area_signed(vertices))


def is_ccw(vertices: list[Vec2]) -> bool:
    return polygon_area_signed(vertices) > 0


def ensure_ccw(vertices: list[Vec2]) -> list[Vec2]:
    if not is_ccw(vertices):
        return list(reversed(vertices))
    return list(vertices)


def classify_vertex(prev: Vec2, curr: Vec2, succ: Vec2) -> str:
    above_prev = curr.y > prev.y
    above_succ = curr.y > succ.y
    below_prev = curr.y < prev.y
    below_succ = curr.y < succ.y

    y_max = above_prev and above_succ
    y_min = below_prev and below_succ

    turn = orientation(prev, curr, succ)

    if y_max and turn > 0:
        return "start"
    if y_max and turn < 0:
        return "split"
    if y_min and turn > 0:
        return "end"
    if y_min and turn < 0:
        return "merge"
    return "regular"


def classify_polygon(vertices: list[Vec2]) -> list[str]:
    n = len(vertices)
    if n < 3:
        return []
    labels = []
    for i in range(n):
        prev = vertices[(i - 1) % n]
        curr = vertices[i]
        succ = vertices[(i + 1) % n]
        labels.append(classify_vertex(prev, curr, succ))
    return labels
