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
        best_edge = None
        best_x = float("-inf")
        for entry in self._entries:
            actual_x = _edge_x_at_y(entry.edge[0], entry.edge[1], self._vertices, self._sweep_y)
            if actual_x < vx and actual_x > best_x:
                best_x = actual_x
                best_edge = entry.edge
        return best_edge

    def snapshot(self) -> list[tuple[tuple[int, int], int | None]]:
        result = []
        for entry in self._entries:
            result.append((entry.edge, self._helpers.get(entry.edge)))
        result.sort(key=lambda e: _edge_x_at_y(e[0][0], e[0][1], self._vertices, self._sweep_y))
        return result

    def edges(self) -> list[tuple[int, int]]:
        return [e.edge for e in self._entries]


def _edge(i: int, n: int) -> tuple[int, int]:
    return (i, (i + 1) % n)


PSEUDOCODE_SEGMENTS = {
    "start": [
        [("Insert ", None), ("ei", "ei_curr"), (" in T and set ", None), ("helper(ei)", "ei_curr"), (" to ", None), ("vi", "vi")],
    ],
    "end": [
        [("if ", None), ("helper(ei-1)", "helper_ei_prev"), (" is a merge vertex:", None)],
        [("  then add diagonal ", None), ("vi", "vi"), (" -> ", None), ("helper(ei-1)", "helper_ei_prev")],
        [("Delete ", None), ("ei-1", "ei_prev"), (" from T", None)],
    ],
    "split": [
        [("Find ", None), ("ej", "ej"), (" directly left of ", None), ("vi", "vi"), (" in T", None)],
        [("add diagonal ", None), ("vi", "vi"), (" -> ", None), ("helper(ej)", "helper_ej")],
        [("helper(ej)", "helper_ej"), (" <- ", None), ("vi", "vi")],
        [("Insert ", None), ("ei", "ei_curr"), (" in T and set ", None), ("helper(ei)", "ei_curr"), (" to ", None), ("vi", "vi")],
    ],
    "merge": [
        [("if ", None), ("helper(ei-1)", "helper_ei_prev"), (" is a merge vertex:", None)],
        [("  then add diagonal ", None), ("vi", "vi"), (" -> ", None), ("helper(ei-1)", "helper_ei_prev")],
        [("Delete ", None), ("ei-1", "ei_prev"), (" from T", None)],
        [("Find ", None), ("ej", "ej"), (" directly left of ", None), ("vi", "vi"), (" in T", None)],
        [("if ", None), ("helper(ej)", "helper_ej"), (" is a merge vertex:", None)],
        [("  then add diagonal ", None), ("vi", "vi"), (" -> ", None), ("helper(ej)", "helper_ej")],
        [("helper(ej)", "helper_ej"), (" <- ", None), ("vi", "vi")],
    ],
    "regular": [
        [("if interior of P is to the right of ", None), ("vi", "vi"), (":", None)],
        [("  then if ", None), ("helper(ei-1)", "helper_ei_prev"), (" is merge:", None)],
        [("    add diagonal ", None), ("vi", "vi"), (" -> ", None), ("helper(ei-1)", "helper_ei_prev")],
        [("  Delete ", None), ("ei-1", "ei_prev"), (" from T", None)],
        [("  Insert ", None), ("ei", "ei_curr"), (" in T and set ", None), ("helper(ei)", "ei_curr"), (" to ", None), ("vi", "vi")],
        [("else Find ", None), ("ej", "ej"), (" directly left of ", None), ("vi", "vi"), (" in T", None)],
        [("  if ", None), ("helper(ej)", "helper_ej"), (" is merge:", None)],
        [("    add diagonal ", None), ("vi", "vi"), (" -> ", None), ("helper(ej)", "helper_ej")],
        [("helper(ej)", "helper_ej"), (" <- ", None), ("vi", "vi")],
    ],
}


@dataclass
class StepResult:
    vi: int
    vtype: str
    pseudocode_key: str
    tree_before: list[tuple[tuple[int, int], int | None]]
    tree_after: list[tuple[tuple[int, int], int | None]]
    diagonals_before: list[tuple[int, int]]
    diagonals_after: list[tuple[int, int]]
    ei_prev: tuple[int, int]
    ei_curr: tuple[int, int]
    helper_ei_prev: int | None
    predecessor_edge: tuple[int, int] | None
    predecessor_helper: int | None
    active_lines: list[int]


def _add_diag(diagonals, a, b):
    if a == b:
        return
    d = (min(a, b), max(a, b))
    if d not in diagonals:
        diagonals.append(d)


def step_vertex(T, vertices, labels, n, vi, diagonals):
    vtype = labels[vi]
    prev_i = (vi - 1) % n
    next_i = (vi + 1) % n
    ei_prev = _edge(prev_i, n)
    ei_curr = _edge(vi, n)

    T.set_sweep_y(vertices[vi].y)
    tree_before = T.snapshot()
    diags_before = list(diagonals)

    helper_ei_prev = T.get_helper(ei_prev)
    predecessor_edge = T.predecessor(vi)
    predecessor_helper = T.get_helper(predecessor_edge) if predecessor_edge else None
    active_lines = []
    diags_added = []

    if vtype == "start":
        active_lines = [0]
        T.insert(ei_curr, vi)

    elif vtype == "end":
        active_lines = [0, 2]
        if helper_ei_prev is not None and labels[helper_ei_prev] == "merge":
            _add_diag(diagonals, vi, helper_ei_prev)
            active_lines.append(1)
        T.delete(ei_prev)

    elif vtype == "split":
        active_lines = [0, 1, 2, 3]
        if predecessor_edge is not None:
            h = T.get_helper(predecessor_edge)
            if h is not None:
                _add_diag(diagonals, vi, h)
            T.set_helper(predecessor_edge, vi)
        T.insert(ei_curr, vi)

    elif vtype == "merge":
        active_lines = [0, 2, 3, 6]
        if helper_ei_prev is not None and labels[helper_ei_prev] == "merge":
            _add_diag(diagonals, vi, helper_ei_prev)
            active_lines.append(1)
        T.delete(ei_prev)
        if predecessor_edge is not None:
            h = T.get_helper(predecessor_edge)
            if h is not None and labels[h] == "merge":
                _add_diag(diagonals, vi, h)
                active_lines.append(5)
            T.set_helper(predecessor_edge, vi)

    elif vtype == "regular":
        on_left = above(vertices[prev_i], vertices[vi])
        if on_left:
            active_lines = [0, 1, 3, 4]
            if helper_ei_prev is not None and labels[helper_ei_prev] == "merge":
                _add_diag(diagonals, vi, helper_ei_prev)
                active_lines.append(2)
            T.delete(ei_prev)
            T.insert(ei_curr, vi)
        else:
            active_lines = [0, 5, 6, 8]
            if predecessor_edge is not None:
                h = T.get_helper(predecessor_edge)
                if h is not None and labels[h] == "merge":
                    _add_diag(diagonals, vi, h)
                    active_lines.append(7)
                T.set_helper(predecessor_edge, vi)

    return StepResult(
        vi=vi,
        vtype=vtype,
        pseudocode_key=vtype,
        tree_before=tree_before,
        tree_after=T.snapshot(),
        diagonals_before=diags_before,
        diagonals_after=list(diagonals),
        ei_prev=ei_prev,
        ei_curr=ei_curr,
        helper_ei_prev=helper_ei_prev,
        predecessor_edge=predecessor_edge,
        predecessor_helper=predecessor_helper,
        active_lines=active_lines,
    )


def make_monotone(vertices: list[Vec2]) -> list[tuple[int, int]]:
    n = len(vertices)
    if n < 3:
        return []

    labels = classify_polygon(vertices)

    indices = list(range(n))
    indices.sort(key=lambda i: (-vertices[i].y, vertices[i].x))

    T = StatusTree(vertices)
    diagonals: list[tuple[int, int]] = []

    for vi in indices:
        step_vertex(T, vertices, labels, n, vi, diagonals)

    return diagonals
