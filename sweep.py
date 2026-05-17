from __future__ import annotations

import bisect
from dataclasses import dataclass, field

from geometry import Vec2, above, classify_polygon


def _edge_x_at_y(a: int, b: int, vertices: list[Vec2], sweep_y: float) -> float:
    va, vb = vertices[a], vertices[b]
    if va.y == vb.y:
        return (va.x + vb.x) / 2
    if sweep_y >= max(va.y, vb.y):
        return va.x if va.y > vb.y else vb.x
    if sweep_y <= min(va.y, vb.y):
        return vb.x if va.y > vb.y else va.x
    t = (sweep_y - vb.y) / (va.y - vb.y)
    return va.x * t + vb.x * (1 - t)


@dataclass(order=True)
class SweepNode:
    x: float
    edge: tuple[int, int] = field(compare=False)


class StatusTree:
    def __init__(self, vertices: list[Vec2]):
        self._entries: list[SweepNode] = []
        self._helpers: dict[tuple[int, int], int] = {}
        self._vertices = vertices
        self._sweep_y = float("inf")

    def set_sweep_y(self, y: float):
        self._sweep_y = y

    def _x(self, edge: tuple[int, int]) -> float:
        return _edge_x_at_y(edge[0], edge[1], self._vertices, self._sweep_y)

    def insert(self, edge: tuple[int, int], helper: int):
        x = self._x(edge)
        bisect.insort(self._entries, SweepNode(x, edge))
        self._helpers[edge] = helper

    def delete(self, edge: tuple[int, int]):
        for i, entry in enumerate(self._entries):
            if entry.edge == edge:
                self._entries.pop(i)
                break
        self._helpers.pop(edge, None)

    def get_helper(self, edge: tuple[int, int]) -> int | None:
        return self._helpers.get(edge)

    def set_helper(self, edge: tuple[int, int], helper: int):
        if edge in self._helpers:
            self._helpers[edge] = helper

    def predecessor(self, vi: int) -> tuple[int, int] | None:
        vx = self._vertices[vi].x
        i = bisect.bisect_left(self._entries, SweepNode(vx, ()))
        if i > 0:
            return self._entries[i - 1].edge
        return None


def _edge(i: int, n: int) -> tuple[int, int]:
    return (i, (i + 1) % n)


def make_monotone(vertices: list[Vec2]) -> list[tuple[int, int]]:
    n = len(vertices)
    if n < 3:
        return []

    labels = classify_polygon(vertices)

    indices = list(range(n))
    indices.sort(key=lambda i: (-vertices[i].y, vertices[i].x))

    Tree = StatusTree(vertices)
    diagonals: list[tuple[int, int]] = []

    def add_diag(a: int, b: int):
        if a == b:
            return
        d = (min(a, b), max(a, b))
        if d not in diagonals:
            diagonals.append(d)

    for vi in indices:
        Tree.set_sweep_y(vertices[vi].y)
        vtype = labels[vi]
        prev_i = (vi - 1) % n
        next_i = (vi + 1) % n
        ei_prev = _edge(prev_i, n)
        ei_curr = _edge(vi, n)

        if vtype == "start":
            Tree.insert(ei_curr, vi)

        elif vtype == "end":
            h = Tree.get_helper(ei_prev)
            if h and labels[h] == "merge":
                add_diag(vi, h)
            Tree.delete(ei_prev)

        elif vtype == "split":
            left = Tree.predecessor(vi)
            if left:
                h = Tree.get_helper(left)
                if h:
                    add_diag(vi, h)
                Tree.set_helper(left, vi)
            Tree.insert(ei_curr, vi)

        elif vtype == "merge":
            h = Tree.get_helper(ei_prev)
            if h and labels[h] == "merge":
                add_diag(vi, h)
            Tree.delete(ei_prev)
            left = Tree.predecessor(vi)
            if left:
                h = Tree.get_helper(left)
                if h and labels[h] == "merge":
                    add_diag(vi, h)
                Tree.set_helper(left, vi)

        elif vtype == "regular":
            on_left_chain = above(vertices[prev_i], vertices[vi])
            if on_left_chain:
                h = Tree.get_helper(ei_prev)
                if h and labels[h] == "merge":
                    add_diag(vi, h)
                Tree.delete(ei_prev)
                Tree.insert(ei_curr, vi)
            else:
                left = Tree.predecessor(vi)
                if left:
                    h = Tree.get_helper(left)
                    if h and labels[h] == "merge":
                        add_diag(vi, h)
                    Tree.set_helper(left, vi)

    return diagonals
