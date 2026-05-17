from __future__ import annotations

from dataclasses import dataclass, field

from geometry import Vec2, classify_polygon, ensure_ccw
from sweep import StatusTree, StepResult, step_vertex, _edge


@dataclass
class TutorialState:
    vertices: list[Vec2]
    labels: list[str]
    n: int
    processing_order: list[int]
    T: StatusTree
    diagonals: list[tuple[int, int]]
    current_index: int
    history: list[StepResult]

    @classmethod
    def create(cls, grid_vertices: list[tuple[float, float]]) -> TutorialState:
        vecs = [Vec2(gx, gy) for gx, gy in grid_vertices]
        ccw = ensure_ccw(vecs)
        labels = classify_polygon(ccw)
        n = len(ccw)
        indices = list(range(n))
        indices.sort(key=lambda i: (-ccw[i].y, ccw[i].x))
        return cls(
            vertices=ccw,
            labels=labels,
            n=n,
            processing_order=indices,
            T=StatusTree(ccw),
            diagonals=[],
            current_index=0,
            history=[],
        )

    def at_start(self) -> bool:
        return self.current_index == 0

    def at_end(self) -> bool:
        return self.current_index >= len(self.processing_order)

    def current_step(self) -> StepResult | None:
        if self.at_end():
            return None
        vi = self.processing_order[self.current_index]
        return step_vertex(
            self.T, self.vertices, self.labels, self.n, vi, self.diagonals,
        )

    def preview(self) -> StepResult | None:
        if self.at_end():
            return None
        vi = self.processing_order[self.current_index]

        T = StatusTree(self.vertices)
        T.set_sweep_y(self.vertices[vi].y)

        if self.history:
            last = self.history[-1]
            for edge, helper in last.tree_after:
                T.insert(edge, helper if helper is not None else 0)

        diags = list(self.diagonals)
        return step_vertex(T, self.vertices, self.labels, self.n, vi, diags)

    def advance(self) -> StepResult | None:
        if self.at_end():
            return None
        step = step_vertex(
            self.T, self.vertices, self.labels, self.n,
            self.processing_order[self.current_index], self.diagonals,
        )
        self.history.append(step)
        self.current_index += 1
        return step

    def undo(self):
        if not self.history:
            return
        self.current_index -= 1
        step = self.history.pop()
        self.T = StatusTree(self.vertices)
        self.diagonals = list(step.diagonals_before)
        for entry in step.tree_before:
            edge, helper = entry
            if helper is not None:
                self.T.insert(edge, helper)
            else:
                self.T.insert(edge, 0)

    @property
    def total_steps(self) -> int:
        return len(self.processing_order)

    @property
    def step_number(self) -> int:
        return self.current_index + 1 if not self.at_end() else self.total_steps
